# Bulk QR Code Generator

[![GitHub Stars](https://img.shields.io/github/stars/Kishoraditya/bulk_qr_generator?style=social)](https://github.com/Kishoraditya/bulk_qr_generator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A powerful, free web application for generating multiple QR codes from spreadsheet data in seconds. Perfect for businesses, event organizers, inventory management, and creative projects.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
  - [Data Input Options](#data-input-options)
  - [QR Code Customization](#qr-code-customization)
  - [Output Formats](#output-formats)
  - [User Experience](#user-experience)
- [Installation](#installation)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
  - [Heroku Deployment](#heroku-deployment)
- [Usage Guide](#usage-guide)
- [Applications](#applications)
- [Advanced Configuration](#advanced-configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Future Enhancements](#future-enhancements)
- [License](#license)
- [Privacy](#privacy)
- [Support](#support)
- [Acknowledgements](#acknowledgements)

## Overview

Bulk QR Code Generator helps you create multiple QR codes from spreadsheet data with just a few clicks. Whether you need QR codes for inventory management, event tickets, product labeling, or marketing campaigns, this tool makes the process simple and efficient.

**Live Demo:** [https://bulk-qr-generator.herokuapp.com](https://bulk-qr-generator.herokuapp.com) (Coming Soon)

## Key Features

### Data Input Options

- **Versatile File Support**: Excel (.xlsx, .xls) and CSV file formats
- **Column Selection**: Choose any column by index for QR code content
- **Flexible Processing**: Process all rows or limit to a specific number
- **Data Cleaning**: Automatic handling of blank rows and data validation

### QR Code Customization

- **Multiple Generation Methods**:
  - Standard QR codes for everyday use
  - High-quality QR codes using Segno library for improved scanning
  - Borderless QR codes for modern applications
- **Visual Adjustments**:
  - Adjustable QR code size (minimum 50px for reliability)
  - Configurable error correction levels (L, M, Q, H)
  - Optional text labels below QR codes
  - Custom content formatting options

### Output Formats

- **PDF Output**: Generate a PDF with all QR codes arranged in a grid
- **Image Archive**: Download a ZIP file with individual QR code images
- **Dual Format**: Option to download both formats simultaneously
- **Layout Control**:
  - Adjustable page margins
  - Configurable spacing between QR codes
  - Control over QR code borders and padding
  - Page numbering options for multi-page outputs
  - Responsive grid layout that adapts to QR code size

### User Experience

- **Modern Interface**: Clean, responsive Bootstrap design
- **Real-time Feedback**: Form validation with helpful tooltips
- **Progress Indicators**: Loading animations during processing
- **Results Dashboard**: Detailed statistics about generated QR codes
- **Mobile Compatibility**: Fully functional on smartphones and tablets

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/Kishoraditya/bulk_qr_generator.git
cd bulk_qr_generator

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Access the application at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

### Docker Deployment

```bash
# Build the Docker image
docker build -t bulk-qr-generator .

# Run the container
docker run -p 5000:5000 bulk-qr-generator
```

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Deploy to Heroku
git push heroku main
```

## Usage Guide

1. **Prepare Your Data**
   - Create an Excel (.xlsx, .xls) or CSV file with your data
   - Ensure the column containing QR code content has valid data
   - Note the column index (starting from 0) for the QR code content

2. **Upload and Configure**
   - Upload your file using the file selector
   - Specify the column index for QR code content
   - Choose whether to process all rows or limit to a specific number
   - Customize QR code appearance (size, error correction, labels)
   - Adjust page layout settings

3. **Generate and Download**
   - Click the "Generate QR Codes" button
   - Wait for processing to complete
   - Download your QR codes in PDF format, ZIP file, or both
   - Review the statistics about your generated QR codes

## Applications

### Business & Marketing

- **Product Packaging**: Link to product information, tutorials, or warranty registration
- **Business Cards**: Share contact information instantly
- **Print Materials**: Enhance brochures, flyers, and posters with interactive elements
- **Coupons & Promotions**: Create scannable discount codes or special offers
- **Social Media Marketing**: Generate QR codes linking to profiles or specific campaigns

### Events & Hospitality

- **Event Tickets**: Streamline check-in with unique QR codes
- **Conference Badges**: Quick access to attendee information
- **Restaurant Menus**: Link to digital menus, specials, or ordering systems
- **Hotel Information**: Provide guests with easy access to services and amenities
- **Event Feedback**: Create QR codes linking to survey forms

### Retail & Inventory

- **Inventory Management**: Track products throughout the supply chain
- **Price Tags**: Create price tags with scannable product details
- **Shelf Labels**: Provide additional product information or stock status
- **Asset Tracking**: Monitor equipment location and maintenance history
- **Warehouse Organization**: Improve logistics with location-coded QR systems

### Education & Non-Profit

- **Educational Materials**: Enhance learning with links to additional resources
- **Attendance Tracking**: Simplify student or member check-in
- **Donation Collection**: Create QR codes for donation pages
- **Certificate Verification**: Add verification links to certificates
- **Campus Navigation**: Help visitors find their way around facilities

### Creative & Personal

- **Tattoos**: Create scannable art with personal meaning
- **Art Installations**: Add interactive elements to exhibitions
- **Personal Branding**: Share portfolios or personal websites
- **Wedding Invitations**: Link to RSVP forms, registries, or venue directions
- **Home Organization**: Create QR inventory systems for personal collections

### Healthcare

- **Patient Identification**: Improve accuracy in patient identification
- **Medication Information**: Provide detailed medication instructions
- **Medical Equipment**: Track usage and maintenance requirements
- **Health Records**: Quick access to patient history for healthcare providers
- **Health Education**: Link to condition-specific information resources

## Advanced Configuration

### Error Correction Levels

- **L (Low)**: 7% of data can be restored
- **M (Medium)**: 15% of data can be restored
- **Q (Quartile)**: 25% of data can be restored
- **H (High)**: 30% of data can be restored

Higher error correction makes QR codes more reliable but increases density.

### QR Code Quality Types

- **Standard**: Basic QR codes suitable for most needs
- **High Quality**: Enhanced QR codes using Segno library for better scanning reliability
- **Borderless**: Modern, clean QR codes without margins (test scanning before mass production)

## Project Structure

``` markdown

bulk-qr-generator/
├── app.py                # Main Flask application
├── old/                  # Old experimental code
├── utils/
│   ├── __init__.py       # Template directory
│   ├── file_utils.py     # Utility functions for file handling
│   └── qr_generator.py   #  QR code generation logic 
├── templates/
│   ├── index.html        # Main page with form
│   ├── 404.html          # 404 error page
│   ├── 500.html          # 500 error page
│   └── sitemap.xml       # Sitemap
├── static/
│   ├── css/
│   │   └── style.css     # Custom styling
│   ├── img/              # Images
│   └── js/
│       └── script.js     # Frontend functionality
├── build.sh              # Build script
├── .gitignore            # Ignore files and directories
├── guicorn_config.py     # Gunicorn configuration
├── README.md             # Project documentation
└── requirements.txt      # Dependencies
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Future Enhancements

- **Dynamic QR Codes**: Create updatable QR codes that can be modified after distribution
- **web3 based tokenization**: Convert into poaps, nfts and other web3 tokenslive onchain with a click.
- **Analytics & Tracking**: Integrate scan statistics and engagement metrics
- **Branded Templates**: Pre-designed styles with custom frames and colors
- **Animated QR Codes**: Support for animated QR codes that work with modern smartphones
- **Batch Design Editor**: Bulk editing of QR code appearance with live preview
- **AI-Powered Optimization**: Automatic adjustment of settings for optimal scanning reliability
- **Accessibility Features**: Voice-guided interface and screen reader compatibility
- **Multi-language Support**: Internationalization for global accessibility
- **QR Code Security**: Password-protected or authenticated QR code access
- **API Integration**: Connect with third-party services for automated generation
- **Mobile Application**: Native app version for on-the-go QR code creation
- **Offline Mode**: Generate QR codes without internet connection
- **Cloud Synchronization**: Save and access projects across devices
- **Augmented Reality Integration**: AR experiences triggered by QR codes
- **Batch Processing Service**: Background processing for extremely large datasets
- **Enhanced Micro QR Support**: Optimized small QR codes when applicable

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Privacy

This application processes all data locally in your browser and on the server. No data is stored permanently on the server, and all temporary files are deleted after processing.

## Support

If you encounter any issues or have questions, please:

- Open an issue on [GitHub](https://github.com/Kishoraditya/bulk_qr_generator/issues)
- Contact us at [kishoradityasc@gmail.com](mailto:kishoradityasc@gmail.com)

## Acknowledgements

- [Anthropic (ClaudeAI)](https://www.anthropic.com/claude) - Basic code generation and Bug solving
- [Segno](https://segno.readthedocs.io/) - High-quality QR code library
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [pandas](https://pandas.pydata.org/) - Data processing
- [ReportLab](https://www.reportlab.com/) - PDF generation
- [Bootstrap](https://getbootstrap.com/) - Frontend styling

---

Made with ❤️ by [Kishoraditya](https://github.com/Kishoraditya)

⭐️ If you find this project useful, please consider giving it a star on GitHub! ⭐️
