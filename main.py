import fitz  # PyMuPDF

# Open the input PDF file
with fitz.open("input.pdf") as doc:
    # Create a new PDF file to store the extracted data
    with fitz.open() as out_doc:
        # Iterate through each page of the input PDF file
        for page in doc:
            # Extract text from the page
            text = page.get_text()
            # Add the extracted text to the new PDF file
            out_doc.insert_page(fitz.Page(text))

            # Extract images from the page
            images = page.get_images()
            for img in images:
                # Add the extracted image to the new PDF file
                out_doc.insert_page(fitz.Page(img))

            # Extract tables from the page (using a simple table detection algorithm)
            tables = []
            for block in page.get_text_blocks():
                if block.is_table:
                    tables.append(block)
            for table in tables:
                # Add the extracted table to the new PDF file
                out_doc.insert_page(fitz.Page(table))

        # Save the new PDF file
        out_doc.save("output.pdf")
