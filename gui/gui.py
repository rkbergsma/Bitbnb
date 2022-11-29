#gui.py

import PySimpleGUI as sg


def create_new_listing_window():
    layout = [[sg.Text("Enter receive bech32 address: ")],
            [sg.In(size=(50, 1), enable_events=True, key="bech32Addr")],
        
        
            [sg.Text("Enter property price per night: ")],
            [sg.In(size=(50, 1), enable_events=True, key="propertyPrice")],
        
            [sg.Text("Describe your property: ")],
            [sg.In(size=(50, 1), enable_events=True, key="propertyDescription")],

            [sg.Button("OK")]]

    # Create the window
    window = sg.Window("Create New Listing", layout)

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "OK" or event == sg.WIN_CLOSED:
            print(values["bech32Addr"])
            print(values["propertyPrice"])
            print(values["propertyDescription"])
            window.close()
            main()
            break
        if event == "Exit" or event == sg.WIN_CLOSED:
            window.close()
            main()
            break
    window.close()

def browse_posts_window():
    layout = [[sg.Text("post 1: post details ")],
            [sg.Button("Book", key="book1")],
            [sg.Text("post 2: post details ")],
            [sg.Button("Book", key="book2")],
            [sg.Text("post 3: post details ")],
            [sg.Button("Book", key="book3")],
            [sg.Text("post 4: post details ")],
            [sg.Button("Book", key="book4")],
            [sg.Button("OK")]]
    
    # Create the window
    window = sg.Window("Browse Listings", layout)

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "OK" or event == sg.WIN_CLOSED:
            window.close()
            main()
            break
        if event == "Exit" or event == sg.WIN_CLOSED:
            window.close()
            main()
            break
    window.close()


def main():
    layout = [[sg.Button("Create New Listing", key="create_new_listing")],
            [sg.Button("Browse Posts", key="browse_posts")]]
    window = sg.Window("Home", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            window.close()
            break
        if event == "create_new_listing":
            window.close()
            create_new_listing_window()
            break
        if event == "browse_posts":
            window.close()
            browse_posts_window()
            break
#    window.close()

if __name__ == "__main__":
    main()
