import tkinter as tk
import sqlite3
from tkinter import messagebox


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("bus_reservation.db")
cursor = conn.cursor()

# Bookings table
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    phone TEXT NOT NULL,
    bus_no TEXT NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    journey_date TEXT NOT NULL,
    journey_time TEXT NOT NULL,
    seat_no INTEGER NOT NULL,
    fare INTEGER NOT NULL
)
""")

# Buses table
cursor.execute("""
CREATE TABLE IF NOT EXISTS buses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_no TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    time TEXT NOT NULL,
    fare INTEGER NOT NULL
)
""")

conn.commit()


# =========================================================
# DEFAULT BUS DATA
# =========================================================

default_buses = [
    ("KA01AB1234", "Ballari", "Bengaluru", "08:00 AM", 500),
    ("KA02CD5678", "Ballari", "Mysuru", "09:30 AM", 600),
    ("KA03EF9012", "Bengaluru", "Mysuru", "07:00 AM", 350)
]

for bus in default_buses:
    try:
        cursor.execute("""
            INSERT INTO buses
            (bus_no, source, destination, time, fare)
            VALUES (?, ?, ?, ?, ?)
        """, bus)
    except sqlite3.IntegrityError:
        pass

conn.commit()


# =========================================================
# GET BUSES
# =========================================================

def get_buses():

    cursor.execute("""
        SELECT bus_no, source, destination, time, fare
        FROM buses
        ORDER BY id
    """)

    rows = cursor.fetchall()

    buses = []

    for row in rows:

        buses.append({
            "bus_no": row[0],
            "from": row[1],
            "to": row[2],
            "time": row[3],
            "fare": row[4]
        })

    return buses


# =========================================================
# GET BOOKED SEATS
# =========================================================

def get_booked_seats(bus_no, journey_date):

    cursor.execute(
        """
        SELECT seat_no
        FROM bookings
        WHERE bus_no = ? AND journey_date = ?
        """,
        (bus_no, journey_date)
    )

    rows = cursor.fetchall()

    return {row[0] for row in rows}


# =========================================================
# BOOK A BUS
# =========================================================

def book_bus():

    booking_window = tk.Toplevel(window)
    booking_window.title("Book a Bus")
    booking_window.geometry("500x420")

    tk.Label(
        booking_window,
        text="SEARCH BUS",
        font=("Arial", 20, "bold")
    ).pack(pady=25)

    tk.Label(
        booking_window,
        text="From:"
    ).pack()

    from_entry = tk.Entry(
        booking_window,
        width=30
    )
    from_entry.pack(pady=5)

    tk.Label(
        booking_window,
        text="To:"
    ).pack()

    to_entry = tk.Entry(
        booking_window,
        width=30
    )
    to_entry.pack(pady=5)

    tk.Label(
        booking_window,
        text="Journey Date (DD-MM-YYYY):"
    ).pack()

    date_entry = tk.Entry(
        booking_window,
        width=30
    )
    date_entry.pack(pady=5)

    # =====================================================
    # SEARCH BUS
    # =====================================================

    def search_bus():

        source = from_entry.get().strip()
        destination = to_entry.get().strip()
        journey_date = date_entry.get().strip()

        if not source or not destination or not journey_date:

            messagebox.showwarning(
                "Missing Details",
                "Please fill From, To and Journey Date."
            )

            return

        results = []

        for bus in get_buses():

            if (
                bus["from"].lower() == source.lower()
                and
                bus["to"].lower() == destination.lower()
            ):
                results.append(bus)

        result_window = tk.Toplevel(
            booking_window
        )

        result_window.title(
            "Available Buses"
        )

        result_window.geometry(
            "550x450"
        )

        tk.Label(
            result_window,
            text="AVAILABLE BUSES",
            font=("Arial", 20, "bold")
        ).pack(pady=25)

        if results:

            for bus in results:

                bus_text = (
                    f'{bus["bus_no"]}   |   '
                    f'{bus["time"]}   |   '
                    f'₹{bus["fare"]}'
                )

                tk.Button(
                    result_window,
                    text=bus_text,
                    width=45,
                    height=2,
                    command=lambda b=bus, d=journey_date:
                        select_seat(b, d)
                ).pack(pady=10)

        else:

            tk.Label(
                result_window,
                text="No buses found.",
                font=("Arial", 14)
            ).pack(pady=30)

    tk.Button(
        booking_window,
        text="SEARCH BUS",
        width=20,
        command=search_bus
    ).pack(pady=25)


# =========================================================
# SELECT SEAT
# =========================================================

def select_seat(bus, journey_date):

    seat_window = tk.Toplevel(window)

    seat_window.title("Select Seat")
    seat_window.geometry("500x650")

    tk.Label(
        seat_window,
        text="SELECT SEAT",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    tk.Label(
        seat_window,
        text=f'Bus: {bus["bus_no"]}',
        font=("Arial", 12)
    ).pack(pady=5)

    tk.Label(
        seat_window,
        text=f'Route: {bus["from"]} → {bus["to"]}',
        font=("Arial", 12)
    ).pack(pady=5)

    tk.Label(
        seat_window,
        text=f'Date: {journey_date}',
        font=("Arial", 12)
    ).pack(pady=5)

    tk.Label(
        seat_window,
        text="DRIVER",
        font=("Arial", 12, "bold")
    ).pack(pady=15)

    seat_frame = tk.Frame(
        seat_window
    )

    seat_frame.pack()

    selected_seat = tk.StringVar()

    booked = get_booked_seats(
        bus["bus_no"],
        journey_date
    )

    # =====================================================
    # CREATE SEATS
    # =====================================================

    for i in range(1, 21):

        seat = tk.Radiobutton(
            seat_frame,
            text=str(i),
            variable=selected_seat,
            value=str(i),
            width=8,
            height=2
        )

        if i in booked:

            seat.config(
                state="disabled",
                text=f"{i} BOOKED"
            )

        row = (i - 1) // 3
        column = (i - 1) % 3

        seat.grid(
            row=row,
            column=column,
            padx=10,
            pady=8
        )

    # =====================================================
    # PASSENGER DETAILS
    # =====================================================

    def passenger_details():

        if not selected_seat.get():

            messagebox.showwarning(
                "Seat Required",
                "Please select a seat."
            )

            return

        passenger_window = tk.Toplevel(
            seat_window
        )

        passenger_window.title(
            "Passenger Details"
        )

        passenger_window.geometry(
            "500x600"
        )

        tk.Label(
            passenger_window,
            text="PASSENGER DETAILS",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        tk.Label(
            passenger_window,
            text="Name:"
        ).pack()

        name_entry = tk.Entry(
            passenger_window,
            width=30
        )
        name_entry.pack(pady=5)

        tk.Label(
            passenger_window,
            text="Age:"
        ).pack()

        age_entry = tk.Entry(
            passenger_window,
            width=30
        )
        age_entry.pack(pady=5)

        tk.Label(
            passenger_window,
            text="Gender:"
        ).pack()

        gender_entry = tk.Entry(
            passenger_window,
            width=30
        )
        gender_entry.pack(pady=5)

        tk.Label(
            passenger_window,
            text="Phone:"
        ).pack()

        phone_entry = tk.Entry(
            passenger_window,
            width=30
        )
        phone_entry.pack(pady=5)

        tk.Label(
            passenger_window,
            text=f"Journey Date: {journey_date}"
        ).pack(pady=10)

        tk.Label(
            passenger_window,
            text=f"Selected Seat: {selected_seat.get()}"
        ).pack(pady=5)

       # =================================================
        # CONFIRM BOOKING
        # =================================================

        def confirm_booking():

            name = name_entry.get().strip()
            age = age_entry.get().strip()
            gender = gender_entry.get().strip()
            phone = phone_entry.get().strip()

            if not name or not age or not gender or not phone:

                messagebox.showwarning(
                    "Missing Details",
                    "Please fill all passenger details."
                )

                return

            if not age.isdigit():

                messagebox.showwarning(
                    "Invalid Age",
                    "Age must contain numbers only."
                )

                return

            if not phone.isdigit() or len(phone) != 10:

                messagebox.showwarning(
                    "Invalid Phone",
                    "Phone number must contain exactly 10 digits."
                )

                return

            booked_now = get_booked_seats(
                bus["bus_no"],
                journey_date
            )

            if int(selected_seat.get()) in booked_now:

                messagebox.showerror(
                    "Seat Unavailable",
                    "Sorry! This seat has already been booked."
                )

                return

            # SAVE BOOKING

            cursor.execute(
                """
                INSERT INTO bookings
                (
                    name,
                    age,
                    gender,
                    phone,
                    bus_no,
                    source,
                    destination,
                    journey_date,
                    journey_time,
                    seat_no,
                    fare
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    int(age),
                    gender,
                    phone,
                    bus["bus_no"],
                    bus["from"],
                    bus["to"],
                    journey_date,
                    bus["time"],
                    int(selected_seat.get()),
                    bus["fare"]
                )
            )

            conn.commit()

            booking_id = cursor.lastrowid

            # =================================================
            # TICKET
            # =================================================

            ticket_window = tk.Toplevel(
                passenger_window
            )

            ticket_window.title(
                "Booking Confirmed"
            )

            ticket_window.geometry(
                "500x620"
            )

            tk.Label(
                ticket_window,
                text="BUS TICKET",
                font=("Arial", 22, "bold")
            ).pack(pady=20)

            ticket_text = (
                f"Booking ID : {booking_id}\n\n"
                f"Passenger  : {name}\n"
                f"Age        : {age}\n"
                f"Gender     : {gender}\n"
                f"Phone      : {phone}\n\n"
                f"Bus No.    : {bus['bus_no']}\n"
                f"From       : {bus['from']}\n"
                f"To         : {bus['to']}\n"
                f"Date       : {journey_date}\n"
                f"Time       : {bus['time']}\n"
                f"Seat No.   : {selected_seat.get()}\n"
                f"Fare       : ₹{bus['fare']}\n\n"
                f"BOOKING CONFIRMED!"
            )

            tk.Label(
                ticket_window,
                text=ticket_text,
                font=("Arial", 12),
                justify="left"
            ).pack(pady=20)

            tk.Button(
                ticket_window,
                text="CLOSE",
                width=15,
                command=ticket_window.destroy
            ).pack(pady=10)

        tk.Button(
            passenger_window,
            text="CONFIRM BOOKING",
            width=25,
            command=confirm_booking
        ).pack(pady=25)

    tk.Button(
        seat_window,
        text="CONTINUE",
        width=20,
        command=passenger_details
    ).pack(pady=25)


# =========================================================
# MY BOOKINGS
# =========================================================

def my_bookings():

    booking_window = tk.Toplevel(window)

    booking_window.title(
        "My Bookings"
    )

    booking_window.geometry(
        "800x650"
    )

    tk.Label(
        booking_window,
        text="MY BOOKINGS",
        font=("Arial", 22, "bold")
    ).pack(pady=20)

    cursor.execute("""
        SELECT
            id,
            name,
            bus_no,
            source,
            destination,
            journey_date,
            journey_time,
            seat_no,
            fare
        FROM bookings
        ORDER BY id DESC
    """)

    bookings = cursor.fetchall()

    if not bookings:

        tk.Label(
            booking_window,
            text="No bookings found.",
            font=("Arial", 14)
        ).pack(pady=30)

        return

    for booking in bookings:

        booking_frame = tk.Frame(
            booking_window,
            relief="groove",
            borderwidth=2
        )

        booking_frame.pack(
            fill="x",
            padx=20,
            pady=8
        )

        text = (
            f"Booking ID : {booking[0]}\n"
            f"Passenger  : {booking[1]}\n"
            f"Bus        : {booking[2]}\n"
            f"Route      : {booking[3]} → {booking[4]}\n"
            f"Date       : {booking[5]}\n"
            f"Time       : {booking[6]}\n"
            f"Seat       : {booking[7]}\n"
            f"Fare       : ₹{booking[8]}"
        )

        tk.Label(
            booking_frame,
            text=text,
            font=("Arial", 11),
            justify="left"
        ).pack(
            side="left",
            padx=15,
            pady=12
        )

        def cancel_booking(
            booking_id=booking[0],
            frame=booking_frame
        ):

            answer = messagebox.askyesno(
                "Cancel Booking",
                "Are you sure you want to cancel this booking?"
            )

            if not answer:
                return

            cursor.execute(
                "DELETE FROM bookings WHERE id = ?",
                (booking_id,)
            )

            conn.commit()

            frame.destroy()

            messagebox.showinfo(
                "Booking Cancelled",
                "Booking cancelled successfully."
            )

        tk.Button(
            booking_frame,
            text="CANCEL BOOKING",
            command=cancel_booking
        ).pack(
            side="right",
            padx=15
        )


# =========================================================
# MANAGE BUSES
# =========================================================

def manage_buses():

    bus_window = tk.Toplevel(window)

    bus_window.title(
        "Manage Buses"
    )

    bus_window.geometry(
        "850x650"
    )

    tk.Label(
        bus_window,
        text="BUS MANAGEMENT",
        font=("Arial", 22, "bold")
    ).pack(pady=20)


    # =====================================================
    # ADD BUS FRAME
    # =====================================================

    add_frame = tk.Frame(
        bus_window,
        relief="groove",
        borderwidth=2
    )

    add_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )


    tk.Label(
        add_frame,
        text="Add New Bus",
        font=("Arial", 16, "bold")
    ).grid(
        row=0,
        column=0,
        columnspan=2,
        pady=15
    )


    tk.Label(
        add_frame,
        text="Bus Number:"
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=8
    )

    bus_no_entry = tk.Entry(
        add_frame,
        width=25
    )

    bus_no_entry.grid(
        row=1,
        column=1,
        padx=10,
        pady=8
    )


    tk.Label(
        add_frame,
        text="From:"
    ).grid(
        row=2,
        column=0,
        padx=10,
        pady=8
    )

    source_entry = tk.Entry(
        add_frame,
        width=25
    )

    source_entry.grid(
        row=2,
        column=1,
        padx=10,
        pady=8
    )


    tk.Label(
        add_frame,
        text="To:"
    ).grid(
        row=3,
        column=0,
        padx=10,
        pady=8
    )

    destination_entry = tk.Entry(
        add_frame,
        width=25
    )

    destination_entry.grid(
        row=3,
        column=1,
        padx=10,
        pady=8
    )


    tk.Label(
        add_frame,
        text="Time:"
    ).grid(
        row=4,
        column=0,
        padx=10,
        pady=8
    )

    time_entry = tk.Entry(
        add_frame,
        width=25
    )

    time_entry.grid(
        row=4,
        column=1,
        padx=10,
        pady=8
    )


    tk.Label(
        add_frame,
        text="Fare:"
    ).grid(
        row=5,
        column=0,
        padx=10,
        pady=8
    )

    fare_entry = tk.Entry(
        add_frame,
        width=25
    )

    fare_entry.grid(
        row=5,
        column=1,
        padx=10,
        pady=8
    )


    # =====================================================
    # BUS LIST
    # =====================================================

    list_frame = tk.Frame(
        bus_window
    )

    list_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )


    def load_buses():

        for widget in list_frame.winfo_children():
            widget.destroy()

        cursor.execute("""
            SELECT
                id,
                bus_no,
                source,
                destination,
                time,
                fare
            FROM buses
            ORDER BY id
        """)

        bus_rows = cursor.fetchall()

        if not bus_rows:

            tk.Label(
                list_frame,
                text="No buses available.",
                font=("Arial", 14)
            ).pack(pady=20)

            return


        for bus in bus_rows:

            bus_id = bus[0]

            frame = tk.Frame(
                list_frame,
                relief="groove",
                borderwidth=2
            )

            frame.pack(
                fill="x",
                pady=5
            )


            text = (
                f"Bus: {bus[1]}\n"
                f"Route: {bus[2]} → {bus[3]}\n"
                f"Time: {bus[4]}    "
                f"Fare: ₹{bus[5]}"
            )


            tk.Label(
                frame,
                text=text,
                font=("Arial", 11),
                justify="left"
            ).pack(
                side="left",
                padx=15,
                pady=10
            )


            def delete_bus(
                bus_id=bus_id
            ):

                answer = messagebox.askyesno(
                    "Delete Bus",
                    "Are you sure you want to delete this bus?"
                )

                if not answer:
                    return


                cursor.execute(
                    "SELECT bus_no FROM buses WHERE id = ?",
                    (bus_id,)
                )

                selected_bus = cursor.fetchone()

                if selected_bus:

                    bus_number = selected_bus[0]

                    cursor.execute(
                        "SELECT COUNT(*) FROM bookings WHERE bus_no = ?",
                        (bus_number,)
                    )

                    booking_count = cursor.fetchone()[0]

                    if booking_count > 0:

                        messagebox.showerror(
                            "Cannot Delete",
                            "This bus has existing bookings and cannot be deleted."
                        )

                        return


                cursor.execute(
                    "DELETE FROM buses WHERE id = ?",
                    (bus_id,)
                )

                conn.commit()

                load_buses()

                messagebox.showinfo(
                    "Bus Deleted",
                    "Bus deleted successfully."
                )


            tk.Button(
                frame,
                text="DELETE",
                command=delete_bus
            ).pack(
                side="right",
                padx=15
            )
            # =====================================================
    # ADD BUS
    # =====================================================

    def add_bus():

        bus_no = bus_no_entry.get().strip()
        source = source_entry.get().strip()
        destination = destination_entry.get().strip()
        time = time_entry.get().strip()
        fare = fare_entry.get().strip()


        if not bus_no or not source or not destination or not time or not fare:

            messagebox.showwarning(
                "Missing Details",
                "Please fill all bus details."
            )

            return


        if not fare.isdigit():

            messagebox.showwarning(
                "Invalid Fare",
                "Fare must contain numbers only."
            )

            return


        try:

            cursor.execute(
                """
                INSERT INTO buses
                (
                    bus_no,
                    source,
                    destination,
                    time,
                    fare
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    bus_no,
                    source,
                    destination,
                    time,
                    int(fare)
                )
            )

            conn.commit()


        except sqlite3.IntegrityError:

            messagebox.showerror(
                "Duplicate Bus",
                "This bus number already exists."
            )

            return


        bus_no_entry.delete(0, tk.END)
        source_entry.delete(0, tk.END)
        destination_entry.delete(0, tk.END)
        time_entry.delete(0, tk.END)
        fare_entry.delete(0, tk.END)


        load_buses()


        messagebox.showinfo(
            "Bus Added",
            "New bus added successfully."
        )


    tk.Button(
        add_frame,
        text="ADD BUS",
        width=20,
        command=add_bus
    ).grid(
        row=6,
        column=0,
        columnspan=2,
        pady=15
    )


    load_buses()


# =========================================================
# ADMIN LOGIN
# =========================================================

def admin_login():

    login_window = tk.Toplevel(window)

    login_window.title(
        "Admin Login"
    )

    login_window.geometry(
        "450x350"
    )


    tk.Label(
        login_window,
        text="ADMIN LOGIN",
        font=("Arial", 22, "bold")
    ).pack(pady=30)


    tk.Label(
        login_window,
        text="Username:"
    ).pack()


    username_entry = tk.Entry(
        login_window,
        width=30
    )

    username_entry.pack(pady=8)


    tk.Label(
        login_window,
        text="Password:"
    ).pack()


    password_entry = tk.Entry(
        login_window,
        width=30,
        show="*"
    )

    password_entry.pack(pady=8)


    def login():

        username = username_entry.get().strip()
        password = password_entry.get().strip()


        if username == "admin" and password == "admin123":

            login_window.destroy()

            admin_dashboard()

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )


    tk.Button(
        login_window,
        text="LOGIN",
        width=20,
        command=login
    ).pack(pady=25)


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard():

    admin_window = tk.Toplevel(window)

    admin_window.title(
        "Admin Dashboard"
    )

    admin_window.geometry(
        "1000x750"
    )


    tk.Label(
        admin_window,
        text="ADMIN DASHBOARD",
        font=("Arial", 24, "bold")
    ).pack(pady=20)


    # =====================================================
    # STATISTICS
    # =====================================================

    stats_frame = tk.Frame(
        admin_window,
        relief="groove",
        borderwidth=2
    )

    stats_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )


    total_bookings_label = tk.Label(
        stats_frame,
        text="Total Bookings: 0",
        font=("Arial", 13, "bold"),
        width=20
    )

    total_bookings_label.grid(
        row=0,
        column=0,
        padx=8,
        pady=15
    )


    total_revenue_label = tk.Label(
        stats_frame,
        text="Total Revenue: ₹0",
        font=("Arial", 13, "bold"),
        width=20
    )

    total_revenue_label.grid(
        row=0,
        column=1,
        padx=8,
        pady=15
    )


    seats_booked_label = tk.Label(
        stats_frame,
        text="Seats Booked: 0",
        font=("Arial", 13, "bold"),
        width=20
    )

    seats_booked_label.grid(
        row=0,
        column=2,
        padx=8,
        pady=15
    )


    buses_used_label = tk.Label(
        stats_frame,
        text="Buses Used: 0",
        font=("Arial", 13, "bold"),
        width=20
    )

    buses_used_label.grid(
        row=0,
        column=3,
        padx=8,
        pady=15
    )


    # =====================================================
    # UPDATE STATISTICS
    # =====================================================

    def update_statistics():

        cursor.execute(
            "SELECT COUNT(*) FROM bookings"
        )

        total_bookings = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COALESCE(SUM(fare), 0) FROM bookings"
        )

        total_revenue = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COUNT(seat_no) FROM bookings"
        )

        seats_booked = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COUNT(DISTINCT bus_no) FROM bookings"
        )

        buses_used = cursor.fetchone()[0]


        total_bookings_label.config(
            text=f"Total Bookings: {total_bookings}"
        )


        total_revenue_label.config(
            text=f"Total Revenue: ₹{total_revenue}"
        )


        seats_booked_label.config(
            text=f"Seats Booked: {seats_booked}"
        )


        buses_used_label.config(
            text=f"Buses Used: {buses_used}"
        )


    # =====================================================
    # BOOKING LIST
    # =====================================================

    list_frame = tk.Frame(
        admin_window
    )

    list_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )


    def load_bookings():

        for widget in list_frame.winfo_children():

            widget.destroy()


        cursor.execute("""
            SELECT
                id,
                name,
                bus_no,
                source,
                destination,
                journey_date,
                journey_time,
                seat_no,
                fare
            FROM bookings
            ORDER BY id DESC
        """)


        bookings = cursor.fetchall()


        if not bookings:

            tk.Label(
                list_frame,
                text="No bookings available.",
                font=("Arial", 14)
            ).pack(pady=30)

            update_statistics()

            return


        for booking in bookings:

            frame = tk.Frame(
                list_frame,
                relief="groove",
                borderwidth=2
            )

            frame.pack(
                fill="x",
                pady=6
            )


            text = (
                f"ID: {booking[0]}    "
                f"Passenger: {booking[1]}    "
                f"Bus: {booking[2]}\n"
                f"Route: {booking[3]} → {booking[4]}    "
                f"Date: {booking[5]}    "
                f"Time: {booking[6]}    "
                f"Seat: {booking[7]}    "
                f"Fare: ₹{booking[8]}"
            )


            tk.Label(
                frame,
                text=text,
                font=("Arial", 10),
                justify="left"
            ).pack(
                side="left",
                padx=10,
                pady=10
            )


            def delete_booking(
                booking_id=booking[0]
            ):

                answer = messagebox.askyesno(
                    "Delete Booking",
                    "Are you sure you want to delete this booking?"
                )


                if answer:

                    cursor.execute(
                        "DELETE FROM bookings WHERE id = ?",
                        (booking_id,)
                    )

                    conn.commit()

                    load_bookings()


            tk.Button(
                frame,
                text="DELETE",
                command=delete_booking
            ).pack(
                side="right",
                padx=15
            )


        update_statistics()


    # =====================================================
    # ADMIN BUTTONS
    # =====================================================

    button_frame = tk.Frame(
        admin_window
    )

    button_frame.pack(
        pady=15
    )


    tk.Button(
        button_frame,
        text="MANAGE BUSES",
        width=18,
        command=manage_buses
    ).pack(
        side="left",
        padx=8
    )


    tk.Button(
        button_frame,
        text="REFRESH",
        width=15,
        command=load_bookings
    ).pack(
        side="left",
        padx=8
    )


    tk.Button(
        button_frame,
        text="REFRESH STATISTICS",
        width=20,
        command=update_statistics
    ).pack(
        side="left",
        padx=8
    )


    tk.Button(
        button_frame,
        text="LOGOUT",
        width=15,
        command=admin_window.destroy
    ).pack(
        side="left",
        padx=8
    )


    load_bookings()


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()

window.title(
    "Smart Bus Reservation System"
)

window.geometry(
    "800x600"
)


tk.Label(
    window,
    text="SMART BUS RESERVATION SYSTEM",
    font=("Arial", 24, "bold")
).pack(pady=40)


tk.Label(
    window,
    text="Welcome! Book your bus journey easily.",
    font=("Arial", 14)
).pack(pady=10)


# BOOK A BUS

tk.Button(
    window,
    text="Book a Bus",
    width=25,
    command=book_bus
).pack(pady=10)


# MY BOOKINGS

tk.Button(
    window,
    text="My Bookings",
    width=25,
    command=my_bookings
).pack(pady=10)


# ADMIN LOGIN

tk.Button(
    window,
    text="Admin Login",
    width=25,
    command=admin_login
).pack(pady=10)


# EXIT

tk.Button(
    window,
    text="Exit",
    width=25,
    command=window.destroy
).pack(pady=10)


# =========================================================
# START
# =========================================================

window.mainloop()