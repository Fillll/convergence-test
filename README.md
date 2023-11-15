# Convergence test tool

This tool uses OpenAI's API to generate and describe images in an iterative process. It generates an image based on a text prompt, describes it, and then uses the description as a new prompt for the next image. This process continues for a specified number of iterations.

## Features

- **Image Generation**: Utilizes OpenAI's DALL-E model to create images from text prompts.
- **Image Description**: Describes generated images using GPT-4.
- **Iterative Process**: Generates a series of images, each based on the description of the previous one.
- **Continuation Capability**: Can continue from the last image in a previously generated series.

## Prerequisites

- Python 3.x
- OpenAI API Key

## Installation

1. Clone the repository to your local machine.
2. Install the required Python packages:
   ```bash
   pip install openai requests
   ```

## Usage

1. **Set up your OpenAI API key**:
   - Save your API key in a text file, e.g., `openai.key`.

2. **Run the script**:
   ```bash
   python script_name.py -a [API Key File] -g [Generation Prompt] -f [Output Folder] -d [Description Prompt] -n [Number of Iterations]
   ```
   Replace `script_name.py` with the actual script filename.

   **Arguments**:
   - `-a` or `--api`: The file containing the OpenAI API key.
   - `-g` or `--generate-prompt`: Initial prompt for generating images.
   - `-f` or `--folder`: Folder where to store the images.
   - `-d` or `--describe-prompt`: Prompt for describing images. (Default: "Describe the image in all details.")
   - `-n` or `--number`: Number of iterations. (Default: 10)

   **Example**:
   ```bash
   python script_name.py -a openai.key -g "A futuristic cityscape" -f generated_images -d "Describe the image in all details." -n 5
   ```

## Important Notes

- The script will create a new folder if it doesn't exist.
- If the folder already contains images, the script will continue from the last numbered image.

## Disclaimer

This tool uses the OpenAI API, and usage may incur costs based on your OpenAI usage plan.
