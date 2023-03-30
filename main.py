import sys
import pathlib
sys.path.append(str(pathlib.Path().absolute()).split("/src")[0])
from src.web_app import front_page


front_page.run()
