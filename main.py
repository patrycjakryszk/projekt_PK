from tkinter import *
from tkinter import messagebox
import tkintermapview
import requests
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="fleet_app")
from bs4 import BeautifulSoup

from model import companies as companies_data
from model import vehicles as cars_data
from model import drivers as drivers_data

companies: list = []
cars: list = []
drivers: list = []


class Company:
    # Klasa przechowuje dane firmy posiadającej flotę i tworzy jej znacznik na mapie.
    def __init__(self, nazwa: str, rok_zalozenia: int, liczba_pojazdow: int, lokalizacja: str):
        self.nazwa = nazwa
        self.rok_zalozenia = rok_zalozenia
        self.liczba_pojazdow = liczba_pojazdow
        self.lokalizacja = lokalizacja
        self.coordinates = Company.get_coordinates(self)

        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1], text=self.nazwa)

    def get_coordinates(self) -> list:
        location = geolocator.geocode(self.lokalizacja)

        if location is None:
            return [52.2, 21.0]

        return [location.latitude, location.longitude]


class Car:
    # Klasa przechowuje dane pojazdu służbowego i tworzy jego znacznik na mapie.
    def __init__(self, numer_rejestracyjny: str, marka: str, model: str, status: str, firma: str,
                 lokalizacja: str):
        self.numer_rejestracyjny = numer_rejestracyjny
        self.marka = marka
        self.model = model
        self.status = status
        self.firma = firma
        self.lokalizacja = lokalizacja
        self.coordinates = Car.get_coordinates(self)

        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1], text=self.numer_rejestracyjny)

    def get_coordinates(self) -> list:
        location = geolocator.geocode(self.lokalizacja)

        if location is None:
            return [52.2, 21.0]

        return [location.latitude, location.longitude]


class Driver:
    # Klasa przechowuje dane kierowcy firmowego i tworzy jego znacznik na mapie.
    def __init__(self, imie: str, nazwisko: str, stanowisko: str, firma: str, lokalizacja: str):
        self.imie = imie
        self.nazwisko = nazwisko
        self.stanowisko = stanowisko
        self.firma = firma
        self.lokalizacja = lokalizacja
        self.coordinates = Driver.get_coordinates(self)

        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1], text=self.imie)

    def get_coordinates(self) -> list:
        location = geolocator.geocode(self.lokalizacja)

        if location is None:
            return [52.2, 21.0]

        return [location.latitude, location.longitude]


def login():
    # Sprawdza dane logowania i po poprawnym zalogowaniu pokazuje główne sekcje systemu floty.
    login_value = entry_login.get()
    password_value = entry_password.get()

    if login_value == "admin" and password_value == "admin":
        ramka_logowanie.grid_forget()

        ramka_firmy.grid(row=0, column=0, padx=10, pady=10, sticky=N)
        ramka_pojazdy.grid(row=0, column=1, padx=10, pady=10, sticky=N)
        ramka_kierowcy.grid(row=0, column=2, padx=10, pady=10, sticky=N)
        ramka_wyniki.grid(row=1, column=0, padx=10, pady=10, sticky=SW)
        ramka_mapa.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky=SE)
    else:
        messagebox.showerror("Błąd", "Niepoprawny login lub hasło")

# funkcje firm
# Czyści listę firm i wyświetla aktualne firmy posiadające flotę pojazdów.
def show_companies() -> None:
    listbox_firmy.delete(0, END)
    for idx, company in enumerate(companies):
        nazwa = company.nazwa
        listbox_firmy.insert(idx, nazwa)

# Pobiera dane z formularza, dodaje nową firmę i tworzy jej znacznik na mapie.
def add_company():
    nazwa = entry_nazwa_firmy.get()
    rok_zalozenia = entry_rok_zalozenia.get()
    liczba_pojazdow = entry_liczba_pojazdow_firmy.get()
    lokalizacja = entry_lokalizacja_firmy.get()

    new_company = Company(nazwa=nazwa, rok_zalozenia=int(rok_zalozenia),
                                 liczba_pojazdow=int(liczba_pojazdow), lokalizacja=lokalizacja)
    companies.append(new_company)

    entry_nazwa_firmy.delete(0, END)
    entry_rok_zalozenia.delete(0, END)
    entry_liczba_pojazdow_firmy.delete(0, END)
    entry_lokalizacja_firmy.delete(0, END)

    entry_nazwa_firmy.focus()
    show_companies()

# Usuwa zaznaczoną firmę z listy oraz usuwa jej znacznik z mapy.
def remove_company() -> None:
    i = listbox_firmy.index(ACTIVE)
    companies[i].marker.delete()
    companies.pop(i)
    show_companies()

 # Wyświetla szczegóły zaznaczonej firmy i centruje mapę na jej współrzędnych.
def show_company_details():
    i = listbox_firmy.index(ACTIVE)

    nazwa = companies[i].nazwa
    rok_zalozenia = companies[i].rok_zalozenia
    liczba_pojazdow = companies[i].liczba_pojazdow
    lokalizacja = companies[i].lokalizacja
    coordinates = companies[i].coordinates

    label_nazwa_firmy_wartosc.config(text=nazwa)
    label_rok_zalozenia_wartosc.config(text=rok_zalozenia)
    label_liczba_pojazdow_firmy_wartosc.config(text=liczba_pojazdow)
    label_lokalizacja_firmy_wartosc.config(text=lokalizacja)

    map_widget.set_position(coordinates[0], coordinates[1])
    map_widget.set_zoom(12)

# Wstawia dane zaznaczonej firmy do formularza, aby można było je edytować.
def edit_company():
    i = listbox_firmy.index(ACTIVE)

    nazwa = companies[i].nazwa
    rok_zalozenia = companies[i].rok_zalozenia
    liczba_pojazdow = companies[i].liczba_pojazdow
    lokalizacja = companies[i].lokalizacja

    entry_nazwa_firmy.insert(0, nazwa)
    entry_rok_zalozenia.insert(0, rok_zalozenia)
    entry_liczba_pojazdow_firmy.insert(0, liczba_pojazdow)
    entry_lokalizacja_firmy.insert(0, lokalizacja)

    button_dodaj_firme.config(text="Zapisz zmiany", command=lambda: update_company(i))

# Zapisuje zmiany firmy, odświeża jej współrzędne oraz aktualizuje znacznik na mapie.
def update_company(i):
    nazwa = entry_nazwa_firmy.get()
    rok_zalozenia = entry_rok_zalozenia.get()
    liczba_pojazdow = entry_liczba_pojazdow_firmy.get()
    lokalizacja = entry_lokalizacja_firmy.get()

    companies[i].nazwa = nazwa
    companies[i].rok_zalozenia = rok_zalozenia
    companies[i].liczba_pojazdow = liczba_pojazdow
    companies[i].lokalizacja = lokalizacja
    companies[i].coordinates = Company.get_coordinates(companies[i])
    companies[i].marker.delete()
    companies[i].marker = map_widget.set_marker(companies[i].coordinates[0], companies[i].coordinates[1], text=nazwa)

    button_dodaj_firme.config(text="Dodaj firmę", command=add_company)

    entry_nazwa_firmy.delete(0, END)
    entry_rok_zalozenia.delete(0, END)
    entry_liczba_pojazdow_firmy.delete(0, END)
    entry_lokalizacja_firmy.delete(0, END)

    entry_nazwa_firmy.focus()
    show_companies()


# funkcje pojazdów
# Czyści listę pojazdów i wyświetla aktualne samochody ze wszystkich firm.
def show_cars() -> None:
    listbox_pojazdy.delete(0, END)
    for idx, car in enumerate(cars):
        numer_rejestracyjny = car.numer_rejestracyjny
        listbox_pojazdy.insert(idx, numer_rejestracyjny)

# Pobiera dane pojazdu z formularza, dodaje go do listy i tworzy znacznik na mapie.
def add_car():
    numer_rejestracyjny = entry_numer_rejestracyjny.get()
    marka = entry_marka.get()
    model = entry_model.get()
    status = entry_status.get()
    firma = entry_firma_pojazdy.get()
    lokalizacja = entry_lokalizacja_pojazdy.get()

    new_car = Car(numer_rejestracyjny=numer_rejestracyjny, marka=marka, model=model, status=status,
                        firma=firma, lokalizacja=lokalizacja)
    cars.append(new_car)

    entry_numer_rejestracyjny.delete(0, END)
    entry_marka.delete(0, END)
    entry_model.delete(0, END)
    entry_status.delete(0, END)
    entry_firma_pojazdy.delete(0, END)
    entry_lokalizacja_pojazdy.delete(0, END)

    entry_numer_rejestracyjny.focus()
    show_cars()

# Usuwa zaznaczony pojazd z listy oraz usuwa jego znacznik z mapy.
def remove_car() -> None:
    i = listbox_pojazdy.index(ACTIVE)
    cars[i].marker.delete()
    cars.pop(i)
    show_cars()

# Wyświetla szczegóły zaznaczonego pojazdu i centruje mapę na jego lokalizacji.
def show_car_details():
    i = listbox_pojazdy.index(ACTIVE)

    numer_rejestracyjny = cars[i].numer_rejestracyjny
    marka = cars[i].marka
    model = cars[i].model
    status = cars[i].status
    firma = cars[i].firma
    lokalizacja = cars[i].lokalizacja
    coordinates = cars[i].coordinates

    label_numer_rejestracyjny_wartosc.config(text=numer_rejestracyjny)
    label_marka_wartosc.config(text=marka)
    label_model_wartosc.config(text=model)
    label_status_wartosc.config(text=status)
    label_firma_pojazdy_wartosc.config(text=firma)
    label_lokalizacja_pojazdy_wartosc.config(text=lokalizacja)

    map_widget.set_position(coordinates[0], coordinates[1])
    map_widget.set_zoom(12)

# Wstawia dane zaznaczonego pojazdu do formularza, aby można było je edytować.
def edit_car():
    i = listbox_pojazdy.index(ACTIVE)

    numer_rejestracyjny = cars[i].numer_rejestracyjny
    marka = cars[i].marka
    model = cars[i].model
    status = cars[i].status
    firma = cars[i].firma
    lokalizacja = cars[i].lokalizacja

    entry_numer_rejestracyjny.insert(0, numer_rejestracyjny)
    entry_marka.insert(0, marka)
    entry_model.insert(0, model)
    entry_status.insert(0, status)
    entry_firma_pojazdy.insert(0, firma)
    entry_lokalizacja_pojazdy.insert(0, lokalizacja)

    button_dodaj_pojazd.config(text="Zapisz zmiany", command=lambda: update_car(i))

# Zapisuje zmiany pojazdu, odświeża jego współrzędne oraz aktualizuje znacznik na mapie.
def update_car(i):
    numer_rejestracyjny = entry_numer_rejestracyjny.get()
    marka = entry_marka.get()
    model = entry_model.get()
    status = entry_status.get()
    firma = entry_firma_pojazdy.get()
    lokalizacja = entry_lokalizacja_pojazdy.get()

    cars[i].numer_rejestracyjny = numer_rejestracyjny
    cars[i].marka = marka
    cars[i].model = model
    cars[i].status = status
    cars[i].firma = firma
    cars[i].lokalizacja = lokalizacja
    cars[i].coordinates = Car.get_coordinates(cars[i])
    cars[i].marker.delete()
    cars[i].marker = map_widget.set_marker(cars[i].coordinates[0], cars[i].coordinates[1],
                                              text=numer_rejestracyjny)

    button_dodaj_pojazd.config(text="Dodaj pojazd", command=add_car)

    entry_numer_rejestracyjny.delete(0, END)
    entry_marka.delete(0, END)
    entry_model.delete(0, END)
    entry_status.delete(0, END)
    entry_firma_pojazdy.delete(0, END)
    entry_lokalizacja_pojazdy.delete(0, END)

    entry_numer_rejestracyjny.focus()
    show_cars()


# funkcje kierowców

def show_drivers() -> None:
    # Czyści listę kierowców i wyświetla aktualnych kierowców wszystkich firm.
    listbox_kierowcy.delete(0, END)
    for idx, driver in enumerate(drivers):
        imie = driver.imie
        nazwisko = driver.nazwisko
        listbox_kierowcy.insert(idx, imie + " " + nazwisko)


def add_driver():
    # Pobiera dane kierowcy z formularza, dodaje go do listy i tworzy znacznik na mapie.
    imie = entry_imie.get()
    nazwisko = entry_nazwisko.get()
    stanowisko = entry_stanowisko.get()
    firma = entry_firma_kierowcy.get()
    lokalizacja = entry_lokalizacja_kierowcy.get()

    new_driver = Driver(imie=imie, nazwisko=nazwisko, stanowisko=stanowisko, firma=firma,
                            lokalizacja=lokalizacja)
    drivers.append(new_driver)

    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_stanowisko.delete(0, END)
    entry_firma_kierowcy.delete(0, END)
    entry_lokalizacja_kierowcy.delete(0, END)

    entry_imie.focus()
    show_drivers()


def remove_driver() -> None:
    # Usuwa zaznaczonego kierowcę z listy oraz usuwa jego znacznik z mapy.
    i = listbox_kierowcy.index(ACTIVE)
    drivers[i].marker.delete()
    drivers.pop(i)
    show_drivers()


def show_driver_details():
    # Wyświetla szczegóły zaznaczonego kierowcy i centruje mapę na jego lokalizacji.
    i = listbox_kierowcy.index(ACTIVE)

    imie = drivers[i].imie
    nazwisko = drivers[i].nazwisko
    stanowisko = drivers[i].stanowisko
    firma = drivers[i].firma
    lokalizacja = drivers[i].lokalizacja
    coordinates = drivers[i].coordinates

    label_imie_wartosc.config(text=imie)
    label_nazwisko_wartosc.config(text=nazwisko)
    label_stanowisko_wartosc.config(text=stanowisko)
    label_firma_kierowcy_wartosc.config(text=firma)
    label_lokalizacja_kierowcy_wartosc.config(text=lokalizacja)

    map_widget.set_position(coordinates[0], coordinates[1])
    map_widget.set_zoom(12)


def edit_driver():
    # Wstawia dane zaznaczonego kierowcy do formularza, aby można było je edytować.
    i = listbox_kierowcy.index(ACTIVE)

    imie = drivers[i].imie
    nazwisko = drivers[i].nazwisko
    stanowisko = drivers[i].stanowisko
    firma = drivers[i].firma
    lokalizacja = drivers[i].lokalizacja

    entry_imie.insert(0, imie)
    entry_nazwisko.insert(0, nazwisko)
    entry_stanowisko.insert(0, stanowisko)
    entry_firma_kierowcy.insert(0, firma)
    entry_lokalizacja_kierowcy.insert(0, lokalizacja)

    button_dodaj_kierowcy.config(text="Zapisz zmiany", command=lambda: update_driver(i))


def update_driver(i):
    # Zapisuje zmiany kierowcy, odświeża jego współrzędne oraz aktualizuje znacznik na mapie.
    imie = entry_imie.get()
    nazwisko = entry_nazwisko.get()
    stanowisko = entry_stanowisko.get()
    firma = entry_firma_kierowcy.get()
    lokalizacja = entry_lokalizacja_kierowcy.get()

    drivers[i].imie = imie
    drivers[i].nazwisko = nazwisko
    drivers[i].stanowisko = stanowisko
    drivers[i].firma = firma
    drivers[i].lokalizacja = lokalizacja
    drivers[i].coordinates = Driver.get_coordinates(drivers[i])
    drivers[i].marker.delete()
    drivers[i].marker = map_widget.set_marker(drivers[i].coordinates[0], drivers[i].coordinates[1], text=imie)

    button_dodaj_kierowcy.config(text="Dodaj kierowcy", command=add_driver)

    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_stanowisko.delete(0, END)
    entry_firma_kierowcy.delete(0, END)
    entry_lokalizacja_kierowcy.delete(0, END)

    entry_imie.focus()
    show_drivers()


# filtracja mapy

def hide_all_markers():
    # Ukrywa wszystkie znaczniki firm, pojazdów i kierowców na mapie.
    for company in companies:
        company.marker.delete()

    for car in cars:
        car.marker.delete()

    for driver in drivers:
        driver.marker.delete()

# Pokazuje wszystkie obiekty wybranej firmy: firmę, jej samochody i jej kierowców.
# Jeśli pole nazwy firmy jest puste, pokazuje wszystkie obiekty z systemu.
def show_all_markers():

    listbox_wyniki.delete(0, END)
    company_name = entry_wyszukaj_firme.get().strip()

    hide_all_markers()

    for company in companies:
        if company_name == "" or company.nazwa.strip().lower() == company_name.lower():
            company.marker = map_widget.set_marker(
                company.coordinates[0],
                company.coordinates[1],
                text=company.nazwa
            )
            if company_name != "":
                listbox_wyniki.insert(END, "Firma: " + company.nazwa)

    for car in cars:
        if company_name == "" or car.firma.strip().lower() == company_name.lower():
            car.marker = map_widget.set_marker(
                car.coordinates[0],
                car.coordinates[1],
                text=car.numer_rejestracyjny
            )
            if company_name != "":
                listbox_wyniki.insert(END, "Samochód: " + car.numer_rejestracyjny + " - " + car.status)

    for driver in drivers:
        if company_name == "" or driver.firma.strip().lower() == company_name.lower():
            driver.marker = map_widget.set_marker(
                driver.coordinates[0],
                driver.coordinates[1],
                text=driver.imie
            )
            if company_name != "":
                listbox_wyniki.insert(END, "Kierowca: " + driver.imie + " " + driver.nazwisko)

# Pokazuje na mapie tylko firmę wpisaną w polu "Nazwa firmy".
# Jeśli pole nazwy firmy jest puste, pokazuje wszystkie firmy.
def show_only_company_markers():

    listbox_wyniki.delete(0, END)
    company_name = entry_wyszukaj_firme.get().strip()

    hide_all_markers()

    for company in companies:
        if company_name == "" or company.nazwa.strip().lower() == company_name.lower():
            company.marker = map_widget.set_marker(
                company.coordinates[0],
                company.coordinates[1],
                text=company.nazwa
            )
            listbox_wyniki.insert(END, company.nazwa + " - " + company.lokalizacja)


# wyszukiwanie po firmie

def show_company_cars():
    # Wyświetla samochody należące do wpisanej firmy i pokazuje je na mapie.
    listbox_wyniki.delete(0, END)
    company_name = entry_wyszukaj_firme.get().strip()

    hide_all_markers()

    for car in cars:
        firma = car.firma

        if firma.strip().lower() == company_name.lower():
            numer_rejestracyjny = car.numer_rejestracyjny
            status = car.status

            listbox_wyniki.insert(END, numer_rejestracyjny + " - " + status)

            car.marker = map_widget.set_marker(
                car.coordinates[0],
                car.coordinates[1],
                text=car.numer_rejestracyjny
            )

def show_company_drivers():
    # Wyświetla kierowców należących do wpisanej firmy i pokazuje ich na mapie.
    listbox_wyniki.delete(0, END)
    company_name = entry_wyszukaj_firme.get().strip()

    hide_all_markers()

    for driver in drivers:
        firma = driver.firma

        if firma.strip().lower() == company_name.lower():
            imie = driver.imie
            nazwisko = driver.nazwisko
            stanowisko = driver.stanowisko

            listbox_wyniki.insert(END, imie + " " + nazwisko + " - " + stanowisko)

            driver.marker = map_widget.set_marker(
                driver.coordinates[0],
                driver.coordinates[1],
                text=driver.imie
            )


root = Tk()

root.title("System zarządzania flotą samochodów służbowych")
root.geometry("1300x900")

# FRAME
ramka_logowanie = Frame(root)
ramka_firmy = Frame(root)
ramka_pojazdy = Frame(root)
ramka_kierowcy = Frame(root)
ramka_wyniki = Frame(root)
ramka_mapa = Frame(root)

# logowanie

ramka_logowanie.grid(row=0, column=0, padx=500, pady=250)

label_logowanie = Label(ramka_logowanie, text="Logowanie")
label_login = Label(ramka_logowanie, text="Login:")
label_password = Label(ramka_logowanie, text="Hasło:")

entry_login = Entry(ramka_logowanie)
entry_password = Entry(ramka_logowanie, show="*")

button_login = Button(ramka_logowanie, text="Zaloguj", command=login)

label_logowanie.grid(row=0, column=0, columnspan=2)
label_login.grid(row=1, column=0, sticky=W)
entry_login.grid(row=1, column=1)
label_password.grid(row=2, column=0, sticky=W)
entry_password.grid(row=2, column=1)
button_login.grid(row=3, column=0, columnspan=2)

# firmy przyciski

label_firmy = Label(ramka_firmy, text="Firmy posiadające flotę")
listbox_firmy = Listbox(ramka_firmy, width=30)

button_pokaz_firme = Button(ramka_firmy, text="Pokaż szczegóły", command=show_company_details)
button_usun_firme = Button(ramka_firmy, text="Usuń", command=remove_company)
button_edytuj_firme = Button(ramka_firmy, text="Edytuj", command=edit_company)

label_nazwa_firmy = Label(ramka_firmy, text="Nazwa:")
label_rok_zalozenia = Label(ramka_firmy, text="Rok założenia:")
label_liczba_pojazdow_firmy = Label(ramka_firmy, text="Liczba pojazdów:")
label_lokalizacja_firmy = Label(ramka_firmy, text="Lokalizacja:")

entry_nazwa_firmy = Entry(ramka_firmy)
entry_rok_zalozenia = Entry(ramka_firmy)
entry_liczba_pojazdow_firmy = Entry(ramka_firmy)
entry_lokalizacja_firmy = Entry(ramka_firmy)

button_dodaj_firme = Button(ramka_firmy, text="Dodaj firmę", command=add_company)

label_szczegoly_firmy = Label(ramka_firmy, text="Szczegóły firmy")

label_nazwa_firmy_szczegoly = Label(ramka_firmy, text="Nazwa firmy")
label_nazwa_firmy_wartosc = Label(ramka_firmy, text="...")
label_rok_zalozenia_szczegoly = Label(ramka_firmy, text="Rok założenia")
label_rok_zalozenia_wartosc = Label(ramka_firmy, text="...")
label_liczba_pojazdow_firmy_szczegoly = Label(ramka_firmy, text="Liczba pojazdów")
label_liczba_pojazdow_firmy_wartosc = Label(ramka_firmy, text="...")
label_lokalizacja_firmy_szczegoly = Label(ramka_firmy, text="Lokalizacja")
label_lokalizacja_firmy_wartosc = Label(ramka_firmy, text="...")

label_firmy.grid(row=0, column=0, columnspan=3)
listbox_firmy.grid(row=1, column=0, columnspan=3)
button_pokaz_firme.grid(row=2, column=0)
button_usun_firme.grid(row=2, column=1)
button_edytuj_firme.grid(row=2, column=2)

label_nazwa_firmy.grid(row=3, column=0, sticky=W)
entry_nazwa_firmy.grid(row=3, column=1)
label_rok_zalozenia.grid(row=4, column=0, sticky=W)
entry_rok_zalozenia.grid(row=4, column=1)
label_liczba_pojazdow_firmy.grid(row=5, column=0, sticky=W)
entry_liczba_pojazdow_firmy.grid(row=5, column=1)
label_lokalizacja_firmy.grid(row=6, column=0, sticky=W)
entry_lokalizacja_firmy.grid(row=6, column=1)
button_dodaj_firme.grid(row=7, column=0, columnspan=2)

label_nazwa_firmy_szczegoly.grid(row=9, column=0, sticky=W)
label_nazwa_firmy_wartosc.grid(row=9, column=1, sticky=W)
label_rok_zalozenia_szczegoly.grid(row=10, column=0, sticky=W)
label_rok_zalozenia_wartosc.grid(row=10, column=1, sticky=W)
label_liczba_pojazdow_firmy_szczegoly.grid(row=11, column=0, sticky=W)
label_liczba_pojazdow_firmy_wartosc.grid(row=11, column=1, sticky=W)
label_lokalizacja_firmy_szczegoly.grid(row=12, column=0, sticky=W)
label_lokalizacja_firmy_wartosc.grid(row=12, column=1, sticky=W)

# pojazdy przyciski

label_pojazdy = Label(ramka_pojazdy, text="Pojazdy")
listbox_pojazdy = Listbox(ramka_pojazdy, width=30)

button_pokaz_pojazd = Button(ramka_pojazdy, text="Pokaż szczegóły", command=show_car_details)
button_usun_pojazd = Button(ramka_pojazdy, text="Usuń", command=remove_car)
button_edytuj_pojazd = Button(ramka_pojazdy, text="Edytuj", command=edit_car)

label_numer_rejestracyjny = Label(ramka_pojazdy, text="Nr rejestracyjny:")
label_marka = Label(ramka_pojazdy, text="Marka:")
label_model = Label(ramka_pojazdy, text="Model:")
label_status = Label(ramka_pojazdy, text="Status:")
label_firma_pojazdy = Label(ramka_pojazdy, text="Firma:")
label_lokalizacja_pojazdy = Label(ramka_pojazdy, text="Lokalizacja:")

entry_numer_rejestracyjny = Entry(ramka_pojazdy)
entry_marka = Entry(ramka_pojazdy)
entry_model = Entry(ramka_pojazdy)
entry_status = Entry(ramka_pojazdy)
entry_firma_pojazdy = Entry(ramka_pojazdy)
entry_lokalizacja_pojazdy = Entry(ramka_pojazdy)

button_dodaj_pojazd = Button(ramka_pojazdy, text="Dodaj pojazd", command=add_car)

label_szczegoly_pojazdy = Label(ramka_pojazdy, text="Szczegóły pojazdu")

label_numer_rejestracyjny_szczegoly = Label(ramka_pojazdy, text="Nr rejestracyjny:")
label_numer_rejestracyjny_wartosc = Label(ramka_pojazdy, text="...")
label_marka_szczegoly = Label(ramka_pojazdy, text="Marka:")
label_marka_wartosc = Label(ramka_pojazdy, text="...")
label_model_szczegoly = Label(ramka_pojazdy, text="Model:")
label_model_wartosc = Label(ramka_pojazdy, text="...")
label_status_szczegoly = Label(ramka_pojazdy, text="Status:")
label_status_wartosc = Label(ramka_pojazdy, text="...")
label_firma_pojazdy_szczegoly = Label(ramka_pojazdy, text="Firma:")
label_firma_pojazdy_wartosc = Label(ramka_pojazdy, text="...")
label_lokalizacja_pojazdy_szczegoly = Label(ramka_pojazdy, text="Lokalizacja:")
label_lokalizacja_pojazdy_wartosc = Label(ramka_pojazdy, text="...")

label_pojazdy.grid(row=0, column=0, columnspan=3)
listbox_pojazdy.grid(row=1, column=0, columnspan=3)
button_pokaz_pojazd.grid(row=2, column=0)
button_usun_pojazd.grid(row=2, column=1)
button_edytuj_pojazd.grid(row=2, column=2)

label_numer_rejestracyjny.grid(row=3, column=0, sticky=W)
entry_numer_rejestracyjny.grid(row=3, column=1)
label_marka.grid(row=4, column=0, sticky=W)
entry_marka.grid(row=4, column=1)
label_model.grid(row=5, column=0, sticky=W)
entry_model.grid(row=5, column=1)
label_status.grid(row=6, column=0, sticky=W)
entry_status.grid(row=6, column=1)
label_firma_pojazdy.grid(row=7, column=0, sticky=W)
entry_firma_pojazdy.grid(row=7, column=1)
label_lokalizacja_pojazdy.grid(row=8, column=0, sticky=W)
entry_lokalizacja_pojazdy.grid(row=8, column=1)
button_dodaj_pojazd.grid(row=9, column=0, columnspan=2)

label_szczegoly_pojazdy.grid(row=10, column=0, sticky=W)
label_numer_rejestracyjny_szczegoly.grid(row=11, column=0, sticky=W)
label_numer_rejestracyjny_wartosc.grid(row=11, column=1, sticky=W)
label_marka_szczegoly.grid(row=12, column=0, sticky=W)
label_marka_wartosc.grid(row=12, column=1, sticky=W)
label_model_szczegoly.grid(row=13, column=0, sticky=W)
label_model_wartosc.grid(row=13, column=1, sticky=W)
label_status_szczegoly.grid(row=14, column=0, sticky=W)
label_status_wartosc.grid(row=14, column=1, sticky=W)
label_firma_pojazdy_szczegoly.grid(row=15, column=0, sticky=W)
label_firma_pojazdy_wartosc.grid(row=15, column=1, sticky=W)
label_lokalizacja_pojazdy_szczegoly.grid(row=16, column=0, sticky=W)
label_lokalizacja_pojazdy_wartosc.grid(row=16, column=1, sticky=W)

# kierowca przyciski

label_kierowcy = Label(ramka_kierowcy, text="Kierowcy")
listbox_kierowcy = Listbox(ramka_kierowcy, width=30)

button_pokaz_kierowcy = Button(ramka_kierowcy, text="Pokaż szczegóły", command=show_driver_details)
button_usun_kierowcy = Button(ramka_kierowcy, text="Usuń", command=remove_driver)
button_edytuj_kierowcy = Button(ramka_kierowcy, text="Edytuj", command=edit_driver)

label_imie = Label(ramka_kierowcy, text="Imię:")
label_nazwisko = Label(ramka_kierowcy, text="Nazwisko:")
label_stanowisko = Label(ramka_kierowcy, text="Stanowisko:")
label_firma_kierowcy = Label(ramka_kierowcy, text="Firma:")
label_lokalizacja_kierowcy = Label(ramka_kierowcy, text="Lokalizacja:")

entry_imie = Entry(ramka_kierowcy)
entry_nazwisko = Entry(ramka_kierowcy)
entry_stanowisko = Entry(ramka_kierowcy)
entry_firma_kierowcy = Entry(ramka_kierowcy)
entry_lokalizacja_kierowcy = Entry(ramka_kierowcy)

button_dodaj_kierowcy = Button(ramka_kierowcy, text="Dodaj kierowcy", command=add_driver)

label_szczegoly_kierowcy = Label(ramka_kierowcy, text="Szczegóły kierowcy")
label_imie_szczegoly = Label(ramka_kierowcy, text="Imię:")
label_imie_wartosc = Label(ramka_kierowcy, text="...")
label_nazwisko_szczegoly = Label(ramka_kierowcy, text="Nazwisko:")
label_nazwisko_wartosc = Label(ramka_kierowcy, text="...")
label_stanowisko_szczegoly = Label(ramka_kierowcy, text="Stanowisko:")
label_stanowisko_wartosc = Label(ramka_kierowcy, text="...")
label_firma_kierowcy_szczegoly = Label(ramka_kierowcy, text="Firma:")
label_firma_kierowcy_wartosc = Label(ramka_kierowcy, text="...")
label_lokalizacja_kierowcy_szczegoly = Label(ramka_kierowcy, text="Lokalizacja:")
label_lokalizacja_kierowcy_wartosc = Label(ramka_kierowcy, text="...")

label_kierowcy.grid(row=0, column=0, columnspan=3)
listbox_kierowcy.grid(row=1, column=0, columnspan=3)
button_pokaz_kierowcy.grid(row=2, column=0)
button_usun_kierowcy.grid(row=2, column=1)
button_edytuj_kierowcy.grid(row=2, column=2)

label_imie.grid(row=3, column=0, sticky=W)
entry_imie.grid(row=3, column=1)
label_nazwisko.grid(row=4, column=0, sticky=W)
entry_nazwisko.grid(row=4, column=1)
label_stanowisko.grid(row=5, column=0, sticky=W)
entry_stanowisko.grid(row=5, column=1)
label_firma_kierowcy.grid(row=6, column=0, sticky=W)
entry_firma_kierowcy.grid(row=6, column=1)
label_lokalizacja_kierowcy.grid(row=7, column=0, sticky=W)
entry_lokalizacja_kierowcy.grid(row=7, column=1)
button_dodaj_kierowcy.grid(row=8, column=0, columnspan=2)

label_szczegoly_kierowcy.grid(row=9, column=0, sticky=W)

label_imie_szczegoly.grid(row=10, column=0, sticky=W)
label_imie_wartosc.grid(row=10, column=1, sticky=W)
label_nazwisko_szczegoly.grid(row=11, column=0, sticky=W)
label_nazwisko_wartosc.grid(row=11, column=1, sticky=W)
label_stanowisko_szczegoly.grid(row=12, column=0, sticky=W)
label_stanowisko_wartosc.grid(row=12, column=1, sticky=W)
label_firma_kierowcy_szczegoly.grid(row=13, column=0, sticky=W)
label_firma_kierowcy_wartosc.grid(row=13, column=1, sticky=W)
label_lokalizacja_kierowcy_szczegoly.grid(row=14, column=0, sticky=W)
label_lokalizacja_kierowcy_wartosc.grid(row=14, column=1, sticky=W)

# wybieranie po nazwie firmy PRZYCISKI

label_wyszukaj_firme = Label(ramka_wyniki, text="Nazwa firmy:")
entry_wyszukaj_firme = Entry(ramka_wyniki)
button_firmy_mapa = Button(ramka_wyniki, text="Pokaż tylko firmy", command=show_only_company_markers)
button_pojazdy_firmy = Button(ramka_wyniki, text="Pokaż samochody firmy", command=show_company_cars)
button_kierowcy_firmy = Button(ramka_wyniki, text="Pokaż kierowców firmy", command=show_company_drivers)
button_pokaz_wszystko = Button(ramka_wyniki, text="Pokaż wszystko", command=show_all_markers)
listbox_wyniki = Listbox(ramka_wyniki, width=60, height=7)

label_wyszukaj_firme.grid(row=0, column=0)
entry_wyszukaj_firme.grid(row=0, column=1)

button_firmy_mapa.grid(row=0, column=2)
button_pojazdy_firmy.grid(row=0, column=3)
button_kierowcy_firmy.grid(row=0, column=4)
button_pokaz_wszystko.grid(row=0, column=5)

listbox_wyniki.grid(row=1, column=0, columnspan=6)

# mapa

map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=700, height=300, corner_radius=4)
map_widget.set_zoom(6)
map_widget.set_position(52.2, 21.0)

map_widget.grid(row=0, column=0)

#Zapis danych z model w aplikacji i wyswuetlenie

for company in companies_data:
    new_company = Company(
        nazwa=company["nazwa"],
        rok_zalozenia=company["rok_zalozenia"],
        liczba_pojazdow=company["liczba_pojazdow"],
        lokalizacja=company["lokalizacja"]
    )

    companies.append(new_company)

show_companies()

for car in cars_data:
    new_car = Car(
        numer_rejestracyjny=car["numer_rejestracyjny"],
        marka=car["marka"],
        model=car["model"],
        status=car["status"],
        firma=car["firma"],
        lokalizacja=car["lokalizacja"]
    )

    cars.append(new_car)

show_cars()

for driver in drivers_data:
    new_driver = Driver(
        imie=driver["imie"],
        nazwisko=driver["nazwisko"],
        stanowisko=driver["stanowisko"],
        firma=driver["firma"],
        lokalizacja=driver["lokalizacja"]
    )

    drivers.append(new_driver)

show_drivers()

root.mainloop()