from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit


def create_pdf(summary_text):
    # Create an in-memory buffer to hold the PDF data
    buffer = BytesIO()

    # Create a new PDF canvas with A4 page size
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Set margins for the PDF content
    margin_x = 40
    margin_y = 40

    # Start drawing text from top (accounting for top margin)
    current_y = height - margin_y

    # Define the height of each line to space text vertically
    line_height = 15

    # Calculate maximum width for text (page width minus left and right margins)
    max_width = width - 2 * margin_x

    # Split the input summary text by new lines to process line by line
    text_lines = summary_text.split('\n')

    # Padding to add some space from left margin when drawing text
    padding = 3

    # Loop through each line of the summary text
    for line in text_lines:
        # Wrap lines if they exceed max_width to avoid overflow
        wrapped_lines = simpleSplit(line, 'Helvetica', 12, max_width)

        # Draw each wrapped line on the canvas
        for wrapped_line in wrapped_lines:
            # Check if we reached the bottom margin to create a new page
            if current_y <= margin_y:
                c.showPage()  # Start a new PDF page
                current_y = height - margin_y  # Reset vertical position to top

            # Draw the text line at the current x, y position
            c.drawString(margin_x + padding, current_y, wrapped_line)

            # Move down for the next line
            current_y -= line_height

    # Save the PDF content to the buffer
    c.save()

    # Reset buffer cursor to the beginning
    buffer.seek(0)

    # Return the buffer containing the generated PDF
    return buffer
