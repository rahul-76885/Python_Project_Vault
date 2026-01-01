from PIL import Image
import qrcode

# STEP 1: Initialize QRCode object
# We explicitly configure the QR parameters instead of using
# qrcode.make() to gain fine-grained control over:
# - Error correction
# - Size of each QR module
# - Border (quiet zone)
# ERROR_CORRECT_H is chosen because it allows ~30% data loss,
# which is essential when embedding a logo inside the QR.

qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # High fault tolerance
    box_size=10,     # Size (in pixels) of each QR module
    border=4,        # Minimum quiet zone required by QR standard
)

# STEP 2: Add encoded data
# The data can be:
# - URL
# - Text
# - Payment string
# - Any UTF-8 compatible content
# add_data() only stores the data logically.
# It does NOT generate the QR matrix yet.

qr.add_data("https://www.linkedin.com/in/rahul-raj-98a941313/")

# STEP 3: Generate QR matrix
# fit=True instructs the library to automatically select
# the smallest possible QR version that can hold the data.
# This avoids DataOverflowError and makes the code scalable
# for future data size changes.

qr.make(fit=True)

# STEP 4: Render QR as an image
# The QR matrix is now converted into an image using Pillow.
# We convert to RGBA mode to enable transparency support,
# which is critical when overlaying a logo image cleanly.

qr_img = qr.make_image(
    fill_color="black",
    back_color="white"
).convert("RGBA")

# STEP 5: Load and prepare the logo
# The logo is opened using Pillow and converted to RGBA
# so that any transparent background in the logo is preserved.

logo = Image.open("logo.png").convert("RGBA")

# STEP 6: Resize the logo (CRITICAL STEP)
# The logo size must be carefully controlled:
# - Too large → QR becomes unreadable
# - Too small → branding impact is lost
# Industry best practice:
# Logo size should not exceed ~25% of QR area.

qr_width, qr_height = qr_img.size
logo_size = qr_width // 4   # Use 25% of QR area for proper branding
logo = logo.resize((logo_size, logo_size))

# STEP 7: Compute center position for logo placement
# Logos are always placed at the center because:
# - Finder patterns are untouched
# - Timing patterns remain intact
# - Error correction can recover lost modules

pos = (
    (qr_width - logo_size) // 2,
    (qr_height - logo_size) // 2
)

# STEP 8: Overlay the logo onto the QR code
# mask=logo ensures that only non-transparent pixels
# of the logo are pasted, maintaining smooth edges.

qr_img.paste(logo, pos, mask=logo)

# STEP 9: Save the final branded QR code
# The output is a production-ready QR image that:
# - Supports branding
# - Maintains scannability
# - Follows QR encoding standards

qr_img.save("brand_qr.png")
