# product
pyinstaller --add-data assert\*;assert --distpath F:\tmp\grabcourses --paths=F:\code\python\projects\grabCourses\env\Scripts --paths F:\code\python\projects\grabCourses\env\Lib\site-packages -w --name WHUT --onefile .\run.py


# test
pyinstaller --add-data assert\*;assert --distpath F:\tmp\grabcourses --paths=F:\code\python\projects\grabCourses\env\Scripts --paths F:\code\python\projects\grabCourses\env\Lib\site-packages .\run.py