# Infotecs
HTTP-сервер для предоставления информации по географическим объектам:
1.	<<get_geoname>> - метод принимает идентификатор geonameid и возвращает название.
### Пример запроса: 
http://127.0.0.1:8000/get_geoname?geoname_id=12181917
2.	<<get_html>> - метод принимает количество отображаемых на странице городов и саму страницу, возвращая таблицу городов с их информацией.
### Пример запроса: 
http://127.0.0.1:8000/compare_two_geonames?first_geoname=Губники&second_geoname=Жуково
Примечание: 
3.	<<compare_two_geonames>> - метод принимает названия двух городов (на русском языке) и выводит таблицу с информацией о найденных городах, а также более северный из них и сравнивает временную зону, выдавая разницу в часах между городами.
### Пример запроса: 
http://127.0.0.1:8000/get_html?count=5&page=https://ru.wikipedia.org/wiki/Игарка
