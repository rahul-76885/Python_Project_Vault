from market import app

# -------------------------------------------------
# Entry point of the Flask application
# -------------------------------------------------
# This condition checks whether this file is being
# run directly (python run.py) and NOT imported
# into another file.
#
# __name__ == '__main__' means:
# "Start the application only if this file is the
# main program being executed."
# -------------------------------------------------
if __name__ == '__main__':

    # Run the Flask development server
    # debug=True enables:
    # - Automatic server reload on code changes
    # - Detailed error messages in the browser
    #
    # IMPORTANT:
    # debug=True should NEVER be used in production
    app.run(debug=True)
