import controller as ctrl
import model as mdl

def main():
    contacts = mdl.load_contacts() # Завантаження контактів
    print("\033[H\033[J", end='')  # Очищення екрану при запуску
    ctrl.hello()

    while True:
        try:
            cmd = ctrl.get_cmd()
            if not cmd.strip():
                ctrl.unknown_command('')
                continue

            command, args = ctrl.parse_input(cmd)
            ctrl.execute(command, args, contacts)

        except KeyboardInterrupt:
            ctrl.quit()

if __name__ == "__main__":
    main()