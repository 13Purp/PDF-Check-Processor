import os

import easyocr
from pdf2image import convert_from_path
import numpy as np
import re
import pprint


def parse_check_info(page_text):
    """
    Parses OCR text based on a fixed upper/lower layout separated by '#############'.
    - Upper part contains Bank Name and "Platite" account number.
    - Lower part contains exactly two numbers (Serial and Tekući).
    """
    info = {
        "bank_name": None,
        "platite_racun_br": None,
        "broj_tekuceg_racuna": None,
        "serijski_broj": None
    }

    # --- 1. Split the page into upper and lower parts ---
    parts = page_text.split('#############')
    upper_text = parts[0]
    lower_text = parts[1] if len(parts) > 1 else ""

    # --- 2. Process the Upper Part ---
    # Bank name logic remains the same, applied only to the upper text
    bank_pattern = re.compile(
        r"(Erste Bank a\.d\. Novi Sad|BANKA POSTANSKA ŠTEDIONICA|otpbanka|UniCredit Bank |BANCA INTESA|NLB Komercijalna banka)",
        re.IGNORECASE
    )
    match = bank_pattern.search(upper_text)
    if match:
        info["bank_name"] = match.group(1).strip()

    # "Platite" number is always in the upper part
    platite_pattern = re.compile(r"(\d{3}-\d{5,}-\d{2})")
    match = platite_pattern.search(upper_text)
    if match:
        info["platite_racun_br"] = match.group(1)

    # --- 3. Process the Lower Part ---
    # Find all potential numbers (long alphanumeric strings or hyphenated strings)
    number_pattern = re.compile(r"(\b\d{3}\b|\b[\d-]{10,}\w?\b)")
    numbers_found = number_pattern.findall(lower_text)

    final_numbers = []
    if len(numbers_found) == 3:
        # Rule: If there are 3 numbers, concatenate the 2nd and 3rd
        final_numbers = [numbers_found[0], numbers_found[1] + numbers_found[2]]
    elif len(numbers_found) == 2:
        final_numbers = numbers_found
    elif len(numbers_found) == 1:
        # If only one number is found in the lower part, we'll assume it's the serial number
        info["serijski_broj"] = numbers_found[0]

    # Assign the two final numbers to the correct fields
    if len(final_numbers) == 2:
        num1, num2 = final_numbers
        # Heuristic: The number with a hyphen or a known bank prefix is the "tekući račun"
        if '-' in num1 or num1.startswith(('200', '340', '325', '170')):
            info["broj_tekuceg_racuna"] = str(num1)
            info["serijski_broj"] = str(num2)
        else:
            info["broj_tekuceg_racuna"] = str(num2)
            info["serijski_broj"] = num1

    return info
def split_and_print(raw_output):
    # Split the raw output by the "--- Page X ---" delimiter
    pages = re.split(r'--- Page \d+ ---', raw_output)

    # The list to hold all our final, structured data
    all_checks_data = []

    for i, page_content in enumerate(pages):
        if page_content.strip():  # Make sure the page content is not empty
            print(f"Parsing Page {i}...")
            parsed_info = parse_check_info(page_content)
            all_checks_data.append(parsed_info)

    # Pretty print the final results
    print("\n--- PARSED DATA ---")
    pprint.pprint(all_checks_data)
    return all_checks_data
def read(pdf_path):
    try:
        pdf_name =  os.path.basename(pdf_path)

        reader = easyocr.Reader(['rs_latin', 'en'])

        print(f"Converting {pdf_path} to images...")
        images = convert_from_path(pdf_path)
        print(f"Found {len(images)} pages.")

        full_text = ""

        for i, image in enumerate(images):
            print(f"Reading page {i + 1}...")

            width, height = image.size

            upper_crop = image.crop((0, 0, width, height // 3))
            lower_crop = image.crop((0, 2 * height // 3, width-width/5, height-height/15))
            upper_crop.save(f"{pdf_name}_{i + 1}_upper.png")
            lower_crop.save(f"{pdf_name}_{i + 1}_lower.png")

            result_upper = reader.readtext(np.array(upper_crop))
            result_lower = reader.readtext(np.array(lower_crop))

            upper_text = "\n".join([f"{text} (Confidence: {prob:.2%})"
                                    for bbox, text, prob in result_upper if prob > 0.2])

            lower_text = "\n".join([f"{text} (Confidence: {prob:.2%})"
                                    for bbox, text, prob in result_lower if prob > 0.2])

            full_text += f"--- Page {i + 1} ---\n"
            full_text += upper_text + "\n" +"#############"+ "\n" + lower_text + "\n"



        print("\nOCR complete! Text saved to output_easyocr.txt")
        return  full_text


    except Exception as e:
        print(f"An error occurred: {e}")
def parse_from_pdf(pdf_path):
    output=read(pdf_path)
    pdf_name = os.path.basename(pdf_path)
    final_output=split_and_print(output)
    with open(f'{pdf_name}.txt', 'w', encoding='utf-8') as f:
        f.write(str(output))
    return final_output

if __name__ == '__main__':
    pdf_path = 'scanned_document.pdf'
    pdf_name = os.path.basename(pdf_path)
    output=parse_from_pdf(pdf_path)
    with open(f'{pdf_name}.txt', 'w', encoding='utf-8') as f:
        f.write(str(output))

