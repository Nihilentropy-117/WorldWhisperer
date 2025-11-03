def main():
    print("Pathfinder 1e Downtime Profit Calculator for Player-owned Shop")

    # Rooms
    num_rooms = int(input("How many rooms do you have in your shop? "))
    room_earnings = 0
    for i in range(num_rooms):
        roll_or_set = input(f"For room {i + 1}, do you want to enter the result of an earnings roll (e.g., d20+10) or a set earnings value? (Enter 'roll' or 'set'): ")
        room_earning = calculate_earnings(roll_or_set)
        room_earnings += room_earning

    # Employees
    num_employees = int(input("How many employees do you have? "))
    employee_earnings = 0
    for i in range(num_employees):
        roll_or_set = input(f"For employee {i + 1}, do you want to enter the result of an earnings roll (e.g., d20+10) or a set earnings value? (Enter 'roll' or 'set'): ")
        emp_earning = calculate_earnings(roll_or_set)
        employee_earnings += emp_earning

    # Capital spent
    capital_spent = int(input("Enter the amount of capital you spent today (e.g., if you spent 5 Goods, 3 Labor, and 1 Magic, enter 9): "))
    capital_value = capital_spent * 10

    # Total earnings for the day
    daily_earnings = room_earnings + employee_earnings - capital_value

    # Time period
    period = input("Do you want to calculate profit per day, week, or month? (Enter 'day', 'week', or 'month'): ").lower()
    if period == 'week':
        total_profit = daily_earnings * 7
    elif period == 'month':
        total_profit = daily_earnings * 30  # approximating a month as 30 days
    else:
        total_profit = daily_earnings

    # Display the results
    print(f"Total Profit for the {period}: {total_profit} silver pieces")


def calculate_earnings(roll_or_set):
    if roll_or_set == "roll":
        base_roll = int(input("Enter the result of your base roll (e.g., if you rolled d20 and got 15, enter 15): "))
        modifier = int(input("Enter the modifier for the roll (e.g., +10 would be 10): "))
        return base_roll + modifier
    elif roll_or_set == "set":
        return int(input("Enter the set earnings value: "))
    else:
        print("Invalid choice. Assuming 0 earnings.")
        return 0


if __name__ == "__main__":
    main()

9,996.04