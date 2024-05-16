import sys, os, ctypes, platform

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin() and platform.system() == 'Windows':
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
        cmd = f'"{script}" {params}'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, cmd, None, 1)
        sys.exit(0)

run_as_admin()

# Now import Gooey and other modules after the admin check
from gooey import Gooey, GooeyParser
import subprocess, json

variables_file = os.path.join(os.path.expanduser('~'), 'variables.json')  # Save in user's home directory

def modify_system_variable(variable_name, variable_value):
    os_name = platform.system()
    if os_name == 'Windows':
        # Use /M to modify the system-wide environment variable
        subprocess.run(['setx', '/M', variable_name, variable_value], check=True)
    elif os_name in ['Linux', 'Darwin']:  # Darwin is macOS
        print(f"Exporting {variable_name}={variable_value} (Manual operation required for Linux/macOS)")
    else:
        raise ValueError("Unsupported OS")

def save_variable_info(soft_name, variable_name, variable_value):
    try:
        variables = get_variables_info()
        variables.append({"soft_name": soft_name, "variable_name": variable_name, "variable_value": variable_value})
        with open(variables_file, 'w') as f:
            json.dump(variables, f)
    except Exception as e:
        print(f"Error saving variable info: {e}")

def get_variables_info():
    if os.path.exists(variables_file):
        with open(variables_file, 'r') as f:
            return json.load(f)
    return []

def apply_variable(soft_name):
    variables = get_variables_info()
    for variable in variables:
        if variable['soft_name'] == soft_name:
            modify_system_variable(variable['variable_name'], variable['variable_value'])
            break

def delete_variable(soft_name):
    variables = get_variables_info()
    variables = [var for var in variables if var['soft_name'] != soft_name]
    with open(variables_file, 'w') as f:
        json.dump(variables, f)
    get_variables_info()

def edit_variable(old_soft_name, new_soft_name, new_variable_name, new_variable_value):
    variables = get_variables_info()
    for variable in variables:
        if variable['soft_name'] == old_soft_name:
            variable['soft_name'] = new_soft_name
            variable['variable_name'] = new_variable_name
            variable['variable_value'] = new_variable_value
            break
    with open(variables_file, 'w') as f:
        json.dump(variables, f)
    print(f"Variable for {old_soft_name} updated successfully.")

def display_variables():
    variables = get_variables_info()
    if variables:
        print("Stored Variables:")
        for var in variables:
            print(f"{var['soft_name']}: {var['variable_name']} {var['variable_value']}")
    else:
        print("No variables stored.")

@Gooey(program_name="System Variable Manager", default_size=(600, 450))
def main():
    parser = GooeyParser(description="Manage System Environment Variables")
    subs = parser.add_subparsers(help='commands', dest='command')

    # Fetch soft_names dynamically for each parser to ensure it is up to date
    soft_names = [var['soft_name'] for var in get_variables_info()]

    # Action 1: Apply Variable
    apply_parser = subs.add_parser('Apply_Variable', help='Apply variable settings from saved configurations')
    apply_parser.add_argument('SelectedSoft', metavar="Select Software", widget='Dropdown', choices=soft_names, help="Select the software to apply settings for")

    # Action 2: Add or Modify Variable
    create_parser = subs.add_parser('Add_Variable', help='Add a system environment variable')
    create_parser.add_argument('SoftName', metavar="Software Name", help="Software relying on the variable")
    create_parser.add_argument('VariableName', metavar="Variable Name", help="Name of the system environment variable")
    create_parser.add_argument('VariableValue', metavar="Variable Value", help="Value of the system environment variable")

    # Action 3: Delete Variable
    delete_parser = subs.add_parser('Delete_Variable', help='Delete a variable by software name')
    delete_parser.add_argument('SoftNameToDelete', metavar="Software Name", widget='Dropdown', choices=soft_names, help="Select the software name of the variable to delete")

    # Action 4: Edit Variable
    edit_parser = subs.add_parser('Edit_Variable', help='Edit details of an existing system environment variable')
    edit_parser.add_argument('SoftNameToEdit', metavar="Select Software", widget='Dropdown', choices=soft_names,
                             help="Select the software name of the variable to edit")
    edit_parser.add_argument('NewSoftName', metavar="New Software Name", help="New software name for the variable")
    edit_parser.add_argument('NewVariableName', metavar="New Variable Name",
                             help="New name of the system environment variable")
    edit_parser.add_argument('NewVariableValue', metavar="New Variable Value",
                             help="New value of the system environment variable")

    # Action for displaying variables
    display_parser = subs.add_parser('Display_Variables', help='Display all stored variables')

    args = parser.parse_args()
    if args.command == 'Add_Variable':
        save_variable_info(args.SoftName, args.VariableName, args.VariableValue)
    elif args.command == 'Apply_Variable':
        apply_variable(args.SelectedSoft)
    elif args.command == 'Delete_Variable':
        delete_variable(args.SoftNameToDelete)
    elif args.command == 'Edit_Variable':
         edit_variable(args.SoftNameToEdit, args.NewSoftName, args.NewVariableName, args.NewVariableValue)
    elif args.command == 'Display_Variables':
        display_variables()

if __name__ == "__main__":
    main()
