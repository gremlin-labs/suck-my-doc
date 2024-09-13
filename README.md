# Suck My Doc
## Stuff an LLM with all the Docs
By Gremlinlabs

### Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Configuration](#configuration)
7. [Output](#output)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [License](#license)
12. [Disclaimer](#disclaimer)

## Introduction

Suck My Doc is a powerful Python-based tool designed to effortlessly extract and format the documentation of any software project on the web. Whether you're working with AI models that need offline access to documentation or you're looking to archive documentation for posterity, Suck My Doc has got you covered.

## Features

- **Automated Scraping**: Intelligently navigates through documentation sites, following navigation links and crawling relevant pages.
- **Flexible URL Restrictions**: By default, restricts scraping to URLs containing '/docs', with an option to scrape all pages on the domain.
- **Structured Output**: Organizes the scraped content in a well-structured JSON format.
- **Customizable Output**: Saves the JSON file to a 'documentation' subfolder with a filename based on the website's domain.
- **Environment Configuration**: Uses a `.env` file to manage environment-specific variables securely.
- **Solo Mode**: Allows scraping of a single page without crawling the entire site.
- **Section Splitting**: Option to save each documentation section into its own file.
- **Robust Parsing**: Uses BeautifulSoup for more accurate HTML parsing and content extraction.
- **Error Handling**: Implements comprehensive error handling for a more stable scraping experience.

## Prerequisites

- Python 3.7+
- Google Chrome for Testing
- ChromeDriver compatible with your version of Chrome for Testing
- Python packages: selenium, beautifulsoup4, python-dotenv

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/suck-my-doc.git
   cd suck-my-doc
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Download Chrome for Testing and ChromeDriver:
   - Chrome for Testing: [Download](https://googlechromelabs.github.io/chrome-for-testing/)
   - ChromeDriver: Ensure the version matches your Chrome for Testing version.

4. Set up the environment variables:
   - Copy the `.env.example` file to `.env`
   - Edit the `.env` file to include the paths to your ChromeDriver and Chrome for Testing binary:
     ```
     CHROMEDRIVER_PATH=/path/to/your/chromedriver
     CHROME_BINARY_PATH="/path/to/your/Google Chrome for Testing"
     ```

## Usage

Basic usage:
```
python smd.py https://example.com/docs
```

This will scrape the documentation from the given URL, restricting to pages under '/docs'.

### Command-line Arguments

- `base_url`: The base URL of the documentation site to scrape (required).
- `-all`: Scrape all pages on the domain, not just those under '/docs'.
- `-csection`: Save each documentation section into its own file.
- `-solo`: Scrape only the provided documentation URL and then stop.

Example with flags:
```
python smd.py https://example.com/docs -all -csection
```

## Configuration

The script uses a `.env` file for configuration. Ensure this file contains:

```
CHROMEDRIVER_PATH=/path/to/your/chromedriver
CHROME_BINARY_PATH="/path/to/your/Google Chrome for Testing"
```

Replace the paths with the actual locations on your system.

## Output

By default, the script creates a 'documentation' directory in the project folder and saves the scraped data as JSON files:

- Without `-csection` flag: A single JSON file named `{domain}_docs.json`.
- With `-csection` flag: Multiple JSON files, one for each scraped section.

The JSON structure includes:
- `title`: The title of the documentation or section.
- `content`: The main textual content.
- `code_examples`: Any code snippets found in the documentation.
- `faq`: Frequently Asked Questions, if available.

## Advanced Usage

### Scraping Single Pages

Use the `-solo` flag to scrape a single page without crawling:
```
python smd.py https://example.com/docs/specific-page -solo
```

### Custom Selectors

If a site has a unique structure, you may need to adjust the selectors in the `extract_main_content` and `extract_faqs` functions within the script.

## Troubleshooting

1. **ChromeDriver issues**: Ensure the ChromeDriver version matches your Chrome for Testing version.
2. **Permission denied**: Make sure the ChromeDriver and Chrome for Testing binary have execute permissions.
3. **No such file or directory**: Double-check the paths in your `.env` file.
4. **Scraping incomplete**: Some sites may use JavaScript to load content. Consider increasing wait times or implementing JavaScript rendering.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-branch-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

Use this tool responsibly and ensure that you have permission to scrape the target documentation site. Always respect the website's terms of service and `robots.txt` rules. The developers of Suck My Doc are not responsible for any misuse of this tool.
