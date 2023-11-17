import argparse
from openai import OpenAI
import os
import requests
import time
import base64

MAX_DESCRIPTION_TOKENS = 1234
IMAGE_SIZE = "1024x1024"


def encode_image(image_path):
    """
    Encodes the given image file into a base64 string.

    Args:
    image_path (str): Path to the image file.

    Returns:
    str: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def describe_image(image_path, openai_api_key, description_prompt):
    """
    Uses the OpenAI API to describe an image from the given file path.

    Args:
    image_path (str): The path to the image file.
    openai_api_key (str): OpenAI API key.
    description_prompt (str): Prompt to guide the image description.

    Returns:
    str: The description of the image generated by OpenAI API.
    """
    client = OpenAI(api_key=openai_api_key)
    encoded_image = encode_image(image_path)

    # Constructing the message payload for the API request
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": description_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
            ],
        }
    ]

    # Sending the request to the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=messages,
        max_tokens=MAX_DESCRIPTION_TOKENS,
    )

    return response.choices[0].message.content


def generate_an_image_from_prompt(openai_api_key, image_generation_prompt, filename):
    """
    Generates an image from a prompt using the OpenAI API and saves it.

    Args:
    openai_api_key (str): OpenAI API key.
    image_generation_prompt (str): Prompt to generate the image.
    filename (str): Path to save the generated image.
    """
    client = OpenAI(api_key=openai_api_key)

    # Generating the image
    response = client.images.generate(
        model="dall-e-3",
        prompt=image_generation_prompt,
        size=IMAGE_SIZE,
        quality="standard",
        n=1,
    )

    # The API returns the URL of the generated image
    image_url = response.data[0].url

    # Download and save the image
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        with open(filename, "wb") as file:
            file.write(image_response.content)
    else:
        print(f"Failed to download the image from {image_url}")


def main(apikey_filename, generation_prompt, folder_name, description_prompt, number_of_iteration):
    # Open and read the API key from the specified file.
    with open(apikey_filename, "r") as file:
        openai_api_key = file.read().strip()

    # Checking for existing files in the specified folder.
    # The list comprehension iterates over all items in the folder,
    # and includes only those that are files (ignoring directories).
    existing_files = [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f))]

    # If there are existing files, determine the highest numbered file.
    # This is done by splitting each filename at the dot (assuming the format is 'number.extension'),
    # converting the number part to an integer, and finding the maximum value.
    if existing_files:
        highest_number = max([int(f.split('.')[0]) for f in existing_files])
        starting_iteration = highest_number + 1
        print(f'🚨 FOUND EXISTING TEST IN THE FOLDER `{folder_name}`!')
        print(f'Total files in the folder: {len(existing_files)}.')
        print(f'The latest file: {highest_number}.')
        print(f'Will start from iteration: {starting_iteration}.')
    else:
        # If there are no existing files, start from the beginning.
        starting_iteration = 0

    # Special case handling: if starting from scratch (i.e., no existing images),
    # generate the first image based on the initial prompt.
    if starting_iteration == 0:
        generate_an_image_from_prompt(openai_api_key, generation_prompt, f"{folder_name}/000.jpeg")
        starting_iteration = 1

    # Main loop for generating and describing images.
    # This loop starts from either the first iteration (if new) or the next iteration (if continuing).
    for iteration in range(starting_iteration, starting_iteration + number_of_iteration):
        start_time = time.time()  # Record the start time of the iteration.

        # Filenames for the previous and next image.
        # 'zfill(3)' ensures the iteration number is zero-padded to 3 digits.
        prev_image_filename = f"{folder_name}/{str(iteration - 1).zfill(3)}.jpeg"
        next_image_filename = f"{folder_name}/{str(iteration).zfill(3)}.jpeg"

        # Describe the previous image to generate a prompt for the next image.
        description = describe_image(prev_image_filename, openai_api_key, description_prompt)

        # Generate the next image based on the description of the previous one.
        generate_an_image_from_prompt(openai_api_key, description, next_image_filename)

        # Calculate the time spent on this iteration.
        spent_time = time.time() - start_time
        print("-" * 33)
        print(f" Iteration: {str(iteration).zfill(3)}. Time: {spent_time:.3f} s.")
        print("-" * 33)
        print("\n")
        print(description)
        print("\n")


if __name__ == "__main__":
    # Setting up command line arguments
    parser = argparse.ArgumentParser(description="Generate and describe images using OpenAI's API.")
    parser.add_argument("-a", "--api", default="openai.key", help="The file containing the OpenAI API key.")
    parser.add_argument("-g", "--generate-prompt", required=True, help="Initial prompt for generating images.")
    parser.add_argument("-f", "--folder", required=True, help="Folder where to store the images.")
    parser.add_argument("-d", "--describe-prompt", default="Describe the image in all details.", help="The prompt for describing the image.")
    parser.add_argument("-n", "--number", type=int, default=10, help="Number of iterations.")
    args = parser.parse_args()

    # Ensure the folder exists
    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    main(args.api, args.generate_prompt, args.folder, args.describe_prompt, args.number)
