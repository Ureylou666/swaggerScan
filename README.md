# API Scanner Utility

This utility script is designed to help developers and security analysts scan APIs described in a Swagger (OpenAPI) JSON file. It sends requests to each endpoint, checks for sensitive information in the responses, and generates a comprehensive report in Excel format.

## Features

- Sends requests to API endpoints defined in a Swagger JSON file.
- Supports `GET` and `POST` methods.
- Checks for sensitive data (e.g., phone numbers, addresses) in the API responses.
- Generates an Excel report detailing each API's method, URI, status code, sensitivity of the response, and the response schema.

## Prerequisites

Before you can run the script, ensure you have the following prerequisites installed:

- Python 3.6 or higher
- `requests` library
- `pandas` library
- `tqdm` library

You can install the necessary Python libraries using pip:

```bash
pip install requests pandas tqdm
```

## Usage

1. **Prepare Your Swagger JSON File**: Ensure you have a valid Swagger (OpenAPI) JSON file that describes the APIs you want to scan.

2. **Set Up Your Environment**: Make sure Python and the required libraries are installed.

3. **Run the Script**: Execute the script from your terminal or command prompt. You will be prompted to enter the path to your Swagger JSON file and the host address for the API calls.

    ```bash
    python api_scanner.py
    ```

4. **Enter Required Information**:
    - When prompted, enter the **full path** to your Swagger JSON file.
    - Enter the **host address** for the API calls (e.g., `https://api.example.com`).

5. **Review the Results**: After the script finishes running, it will generate an Excel file with the results. The file name is derived from the title of the Swagger documentation and will be printed in the terminal.

## Report Details

The generated Excel report contains the following columns:

- **Method**: The HTTP method used (GET/POST).
- **API URI**: The URI of the API endpoint.
- **Status Code**: The HTTP status code received in response.
- **Contains Sensitive**: Indicates whether the response contains sensitive data.
- **Response Schema**: The schema of the response.

## Contributing

Feel free to fork this repository and submit pull requests to add more features or support additional methods.

## License

[MIT License](LICENSE.md)

---

Remember to replace placeholder texts with actual information relevant to your project, such as the correct path to the Python script if it's not directly in the root directory or any additional steps required for setup.
