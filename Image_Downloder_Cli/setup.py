from setuptools import setup, find_packages

# setup() is used by pip to understand:
# - what your project is
# - how to install it
# - how to expose CLI commands
setup(
    # -------------------------------------------------
    # Name of the package
    #
    # This is the name pip uses for:
    #   pip install image-downloader-cli
    #   pip uninstall image-downloader-cli
    # -------------------------------------------------
    name="image-downloader-cli",

    # -------------------------------------------------
    # Version of your package
    #
    # Used for upgrades, publishing, and dependency
    # management.
    # -------------------------------------------------
    version="1.0.0",

    # -------------------------------------------------
    # Automatically finds all Python packages
    # (folders containing __init__.py)
    #
    # In your case, it finds:
    # image_downloader/
    # -------------------------------------------------
    packages=find_packages(),

    # -------------------------------------------------
    # External libraries required for this package
    #
    # pip will automatically install these
    # -------------------------------------------------
    install_requires=[
        "requests",
    ],

    # -------------------------------------------------
    # CLI ENTRY POINT (MOST IMPORTANT PART)
    #
    # This creates a global command called `imgdl`
    #
    # Meaning:
    #   imgdl  →  image_downloader/cli.py → main()
    #
    # When user types:
    #   imgdl --help
    #
    # Python:
    # 1. Imports image_downloader.cli
    # 2. Calls main()
    # -------------------------------------------------
    entry_points={
        "console_scripts": [
            "imgdl=image_downloader.cli:main"
        ]
    },
)
