"""
Pathfinder 1e Downtime Profit Calculator for Player-owned Shops.
Based on Pathfinder 1e downtime rules.
"""


def calculate_earnings(roll_or_set):
    """
    Calculate earnings from user input (roll or set value).

    Args:
        roll_or_set: Either 'roll' for dice input or 'set' for fixed value

    Returns:
        Integer earnings value
    """
    if roll_or_set.lower() == "roll":
        base_roll = int(input("  Enter base roll result (e.g., if d20 rolled 15, enter 15): "))
        modifier = int(input("  Enter modifier (e.g., +10 would be 10): "))
        return base_roll + modifier
    elif roll_or_set.lower() == "set":
        return int(input("  Enter set earnings value: "))
    else:
        print("  Invalid choice. Assuming 0 earnings.")
        return 0


def shop_calculator_menu():
    """Main interface for shop profit calculator."""
    print("\n" + "="*60)
    print("PATHFINDER 1E SHOP PROFIT CALCULATOR")
    print("="*60)
    print("\nThis calculator helps determine downtime profits for")
    print("player-owned shops based on Pathfinder 1e rules.\n")

    # Rooms
    try:
        num_rooms = int(input("How many rooms in your shop? "))
    except ValueError:
        print("Invalid input. Using 0 rooms.")
        num_rooms = 0

    room_earnings = 0
    for i in range(num_rooms):
        print(f"\nRoom {i + 1}:")
        roll_or_set = input("  Roll or set earnings? (enter 'roll' or 'set'): ").strip()
        room_earning = calculate_earnings(roll_or_set)
        room_earnings += room_earning
        print(f"  → Room {i + 1} earnings: {room_earning} sp")

    # Employees
    try:
        num_employees = int(input("\nHow many employees do you have? "))
    except ValueError:
        print("Invalid input. Using 0 employees.")
        num_employees = 0

    employee_earnings = 0
    for i in range(num_employees):
        print(f"\nEmployee {i + 1}:")
        roll_or_set = input("  Roll or set earnings? (enter 'roll' or 'set'): ").strip()
        emp_earning = calculate_earnings(roll_or_set)
        employee_earnings += emp_earning
        print(f"  → Employee {i + 1} earnings: {emp_earning} sp")

    # Capital spent
    try:
        capital_spent = int(input("\nEnter capital units spent today (Goods + Labor + Magic): "))
    except ValueError:
        print("Invalid input. Using 0 capital.")
        capital_spent = 0

    capital_value = capital_spent * 10  # Each capital unit = 10 sp

    # Calculate daily earnings
    daily_earnings = room_earnings + employee_earnings - capital_value

    # Time period
    print("\nCalculate profit for:")
    print("1. Day")
    print("2. Week")
    print("3. Month")

    period_choice = input("Enter choice (1-3, default=day): ").strip()

    if period_choice == '2':
        period = "week"
        total_profit = daily_earnings * 7
    elif period_choice == '3':
        period = "month"
        total_profit = daily_earnings * 30
    else:
        period = "day"
        total_profit = daily_earnings

    # Display results
    print("\n" + "="*60)
    print("CALCULATION SUMMARY")
    print("="*60)
    print(f"Room earnings:       {room_earnings:>6} sp")
    print(f"Employee earnings:   {employee_earnings:>6} sp")
    print(f"Capital spent:       {-capital_value:>6} sp ({capital_spent} units)")
    print("-" * 60)
    print(f"Daily profit:        {daily_earnings:>6} sp")
    print(f"\nTotal profit ({period}): {total_profit:>6} sp")
    print("="*60)

    # Convert to gold for convenience
    if abs(total_profit) >= 10:
        gp = total_profit / 10
        print(f"                     {gp:>6.1f} gp")
        print("="*60)

    input("\nPress Enter to continue...")


# For standalone testing
if __name__ == "__main__":
    while True:
        shop_calculator_menu()

        again = input("\nCalculate another shop? (y/n): ").strip().lower()
        if again not in ['y', 'yes']:
            break