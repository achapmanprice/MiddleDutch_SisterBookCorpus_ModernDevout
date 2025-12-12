The Sister Books from Master Geert's House (G) and from Diepenveen (D), as well as one published _vite_ from the Lamme van Dies House Book (L) are all available for download as XML files from the Bibliotheek voor de Nederlandse Letteren (DBNL), the digital library for Dutch literature. 

These XML files then needed to be transformed into plain text files, with only the text of the body saved without any of the markup. In other words, this process involves more than just conversion to new file extensions, but rather the removal of a significant amount of material from the XML files (i.e., all markup). 

The Python script xml_to_txt_body.py (uploaded in this repository) needs to be saved in the same location as a folder labeled xml_folder that must also contain all the XML files that need to be transformed. The script provides directions for saving the new .txt files in that same folder. 
