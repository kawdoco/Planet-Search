from solarsystem import SolarSystem

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'planet_db'
}

def main():
    solar_system = SolarSystem(db_config)

    planet_input = input("\nEnter the planet name you want to search (e.g.,Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune): ")
    date_input = input("Enter date and time (YYYY-MM-DD HH:MM): ")

    data = solar_system.calculate_position(planet_input, date_input)

    if data:
        solar_system.display(data)
        solar_system.save_to_db(data, date_input)
    else:
        print("\n  Invalid planet name.\n  Please enter a valid planet (Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune).")

    solar_system.close()

if __name__ == "__main__":
    main()
