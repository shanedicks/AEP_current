# Generated by Django 4.2.4 on 2023-10-05 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0093_student_site_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='city',
            field=models.CharField(choices=[('Abbeville', 'Abbeville'), ('Abita Springs', 'Abita Springs'), ('Addis', 'Addis'), ('Albany', 'Albany'), ('Alexandria', 'Alexandria'), ('Amite', 'Amite'), ('Anacoco', 'Anacoco'), ('Angie', 'Angie'), ('Arcadia', 'Arcadia'), ('Arnaudville', 'Arnaudville'), ('Ashland', 'Ashland'), ('Athens', 'Athens'), ('Atlanta', 'Atlanta'), ('Baker', 'Baker'), ('Baldwin', 'Baldwin'), ('Ball', 'Ball'), ('Basile', 'Basile'), ('Baskin', 'Baskin'), ('Bastrop', 'Bastrop'), ('Baton Rouge', 'Baton Rouge'), ('Belcher', 'Belcher'), ('Benton', 'Benton'), ('Bernice', 'Bernice'), ('Berwick', 'Berwick'), ('Bienville', 'Bienville'), ('Blanchard', 'Blanchard'), ('Bogalusa', 'Bogalusa'), ('Bonita', 'Bonita'), ('Bossier', 'Bossier'), ('Boutte', 'Boutte'), ('Boyce', 'Boyce'), ('Breaux Bridge', 'Breaux Bridge'), ('Broussard', 'Broussard'), ('Brusly', 'Brusly'), ('Bryceland', 'Bryceland'), ('Bunkie', 'Bunkie'), ('Calvin', 'Calvin'), ('Campti', 'Campti'), ('Cankton', 'Cankton'), ('Carencro', 'Carencro'), ('Castor', 'Castor'), ('Chalmette', 'Chalmette'), ('Central', 'Central'), ('Chataignier', 'Chataignier'), ('Chatham', 'Chatham'), ('Cheneyville', 'Cheneyville'), ('Choudrant', 'Choudrant'), ('Church Point', 'Church Point'), ('Clarence', 'Clarence'), ('Clarks', 'Clarks'), ('Clayton', 'Clayton'), ('Clinton', 'Clinton'), ('Colfax', 'Colfax'), ('Collinston', 'Collinston'), ('Columbia', 'Columbia'), ('Converse', 'Converse'), ('Cottonport', 'Cottonport'), ('Cotton Valley', 'Cotton Valley'), ('Coushatta', 'Coushatta'), ('Covington', 'Covington'), ('Creola', 'Creola'), ('Crowley', 'Crowley'), ('Cullen', 'Cullen'), ('Delcambre', 'Delcambre'), ('Delhi', 'Delhi'), ('Delta', 'Delta'), ('Denham Springs', 'Denham Springs'), ('DeQuincy', 'DeQuincy'), ('DeRidder', 'DeRidder'), ('Dixie Inn', 'Dixie Inn'), ('Dodson', 'Dodson'), ('Donaldsonville', 'Donaldsonville'), ('Downsville', 'Downsville'), ('Doyline', 'Doyline'), ('Dry Prong', 'Dry Prong'), ('Dubach', 'Dubach'), ('Dubberly', 'Dubberly'), ('Duson', 'Duson'), ('East Hodge', 'East Hodge'), ('Edgefield', 'Edgefield'), ('Elizabeth', 'Elizabeth'), ('Elton', 'Elton'), ('Epps', 'Epps'), ('Erath', 'Erath'), ('Eros', 'Eros'), ('Estherwood', 'Estherwood'), ('Eunice', 'Eunice'), ('Evergreen', 'Evergreen'), ('Farmerville', 'Farmerville'), ('Fenton', 'Fenton'), ('Ferriday', 'Ferriday'), ('Fisher', 'Fisher'), ('Florien', 'Florien'), ('Folsom', 'Folsom'), ('Fordoche', 'Fordoche'), ('Forest', 'Forest'), ('Forest Hill', 'Forest Hill'), ('Franklin', 'Franklin'), ('Franklinton', 'Franklinton'), ('French Settlement', 'French Settlement'), ('Georgetown', 'Georgetown'), ('Gibsland', 'Gibsland'), ('Gilbert', 'Gilbert'), ('Gilliam', 'Gilliam'), ('Glenmora', 'Glenmora'), ('Golden Meadow', 'Golden Meadow'), ('Goldonna', 'Goldonna'), ('Gonzales', 'Gonzales'), ('Grambling', 'Grambling'), ('Gramercy', 'Gramercy'), ('Grand Cane', 'Grand Cane'), ('Grand Coteau', 'Grand Coteau'), ('Grand Isle', 'Grand Isle'), ('Grayson', 'Grayson'), ('Greensburg', 'Greensburg'), ('Greenwood', 'Greenwood'), ('Gretna', 'Gretna'), ('Grosse Tete', 'Grosse Tete'), ('Gueydan', 'Gueydan'), ('Hall Summit', 'Hall Summit'), ('Hammond', 'Hammond'), ('Harahan', 'Harahan'), ('Harrisonburg', 'Harrisonburg'), ('Haughton', 'Haughton'), ('Haynesville', 'Haynesville'), ('Heflin', 'Heflin'), ('Henderson', 'Henderson'), ('Hessmer', 'Hessmer'), ('Hodge', 'Hodge'), ('Homer', 'Homer'), ('Hornbeck', 'Hornbeck'), ('Hosston', 'Hosston'), ('Houma', 'Houma'), ('Ida', 'Ida'), ('Independence', 'Independence'), ('Iota', 'Iota'), ('Iowa', 'Iowa'), ('Jackson', 'Jackson'), ('Jamestown', 'Jamestown'), ('Jeanerette', 'Jeanerette'), ('Jean Lafitte', 'Jean Lafitte'), ('Jena', 'Jena'), ('Jennings', 'Jennings'), ('Jonesboro', 'Jonesboro'), ('Jonesville', 'Jonesville'), ('Junction', 'Junction'), ('Kaplan', 'Kaplan'), ('Keachi', 'Keachi'), ('Keithville', 'Keithville'), ('Kenner', 'Kenner'), ('Kentwood', 'Kentwood'), ('Kilbourne', 'Kilbourne'), ('Killian', 'Killian'), ('Kinder', 'Kinder'), ('Krotz Springs', 'Krotz Springs'), ('Lafayette', 'Lafayette'), ('Lake Arthur', 'Lake Arthur'), ('Lake Charles', 'Lake Charles'), ('Lake Providence', 'Lake Providence'), ('Lecompte', 'Lecompte'), ('Leesville', 'Leesville'), ('Leonville', 'Leonville'), ('Lillie', 'Lillie'), ('Lisbon', 'Lisbon'), ('Livingston', 'Livingston'), ('Livonia', 'Livonia'), ('Lockport', 'Lockport'), ('Logansport', 'Logansport'), ('Longstreet', 'Longstreet'), ('Loreauville', 'Loreauville'), ('Lucky', 'Lucky'), ('Lutcher', 'Lutcher'), ('McNary', 'McNary'), ('Madisonville', 'Madisonville'), ('Mamou', 'Mamou'), ('Mandeville', 'Mandeville'), ('Mangham', 'Mangham'), ('Mansfield', 'Mansfield'), ('Mansura', 'Mansura'), ('Many', 'Many'), ('Maringouin', 'Maringouin'), ('Marion', 'Marion'), ('Marksville', 'Marksville'), ('Martin', 'Martin'), ('Maurice', 'Maurice'), ('Melville', 'Melville'), ('Mermentau', 'Mermentau'), ('Mer Rouge', 'Mer Rouge'), ('Merryville', 'Merryville'), ('Metairie', 'Metairie'), ('Minden', 'Minden'), ('Monroe', 'Monroe'), ('Montgomery', 'Montgomery'), ('Montpelier', 'Montpelier'), ('Mooringsport', 'Mooringsport'), ('Moreauville', 'Moreauville'), ('Morgan City', 'Morgan City'), ('Morganza', 'Morganza'), ('Morse', 'Morse'), ('Mound', 'Mound'), ('Mount Lebanon', 'Mount Lebanon'), ('Napoleonville', 'Napoleonville'), ('Natchez', 'Natchez'), ('Natchitoches', 'Natchitoches'), ('Newellton', 'Newellton'), ('New Iberia', 'New Iberia'), ('New Llano', 'New Llano'), ('New Orleans', 'New Orleans'), ('New Roads', 'New Roads'), ('Noble', 'Noble'), ('North Hodge', 'North Hodge'), ('Norwood', 'Norwood'), ('Oakdale', 'Oakdale'), ('Oak Grove', 'Oak Grove'), ('Oak Ridge', 'Oak Ridge'), ('Oberlin', 'Oberlin'), ('Oil City', 'Oil City'), ('Olla', 'Olla'), ('Opelousas', 'Opelousas'), ('Palmetto', 'Palmetto'), ('Parks', 'Parks'), ('Patterson', 'Patterson'), ('Pearl River', 'Pearl River'), ('Pine Prairie', 'Pine Prairie'), ('Pineville', 'Pineville'), ('Pioneer', 'Pioneer'), ('Plain Dealing', 'Plain Dealing'), ('Plaquemine', 'Plaquemine'), ('Plaucheville', 'Plaucheville'), ('Pleasant Hill', 'Pleasant Hill'), ('Pollock', 'Pollock'), ('Ponchatoula', 'Ponchatoula'), ('Port Allen', 'Port Allen'), ('Port Barre', 'Port Barre'), ('Port Vincent', 'Port Vincent'), ('Powhatan', 'Powhatan'), ('Provencal', 'Provencal'), ('Quitman', 'Quitman'), ('Rayne', 'Rayne'), ('Rayville', 'Rayville'), ('Reeves', 'Reeves'), ('Richmond', 'Richmond'), ('Richwood', 'Richwood'), ('Ridgecrest', 'Ridgecrest'), ('Ringgold', 'Ringgold'), ('Robeline', 'Robeline'), ('Rodessa', 'Rodessa'), ('Rosedale', 'Rosedale'), ('Roseland', 'Roseland'), ('Rosepine', 'Rosepine'), ('Ruston', 'Ruston'), ('St. Francisville', 'St. Francisville'), ('St. Gabriel', 'St. Gabriel'), ('St. Joseph', 'St. Joseph'), ('St. Martinville', 'St. Martinville'), ('Saline', 'Saline'), ('Sarepta', 'Sarepta'), ('Scott', 'Scott'), ('Shongaloo', 'Shongaloo'), ('Shreveport', 'Shreveport'), ('Sibley', 'Sibley'), ('Sicily Island', 'Sicily Island'), ('Sikes', 'Sikes'), ('Simmesport', 'Simmesport'), ('Simpson', 'Simpson'), ('Simsboro', 'Simsboro'), ('Slaughter', 'Slaughter'), ('Slidell', 'Slidell'), ('Sorrento', 'Sorrento'), ('South Mansfield', 'South Mansfield'), ('Spearsville', 'Spearsville'), ('Springfield', 'Springfield'), ('Springhill', 'Springhill'), ('Stanley', 'Stanley'), ('Sterlington', 'Sterlington'), ('Stonewall', 'Stonewall'), ('Sulphur', 'Sulphur'), ('Sun', 'Sun'), ('Sunset', 'Sunset'), ('Tallulah', 'Tallulah'), ('Tangipahoa', 'Tangipahoa'), ('Thibodaux', 'Thibodaux'), ('Tickfaw', 'Tickfaw'), ('Tullos', 'Tullos'), ('Turkey Creek', 'Turkey Creek'), ('Urania', 'Urania'), ('Varnado', 'Varnado'), ('Vidalia', 'Vidalia'), ('Vienna', 'Vienna'), ('Ville Platte', 'Ville Platte'), ('Vinton', 'Vinton'), ('Vivian', 'Vivian'), ('Walker', 'Walker'), ('Washington', 'Washington'), ('Waterproof', 'Waterproof'), ('Welsh', 'Welsh'), ('Westlake', 'Westlake'), ('West Monroe', 'West Monroe'), ('Westwego', 'Westwego'), ('White Castle', 'White Castle'), ('Wilson', 'Wilson'), ('Winnfield', 'Winnfield'), ('Winnsboro', 'Winnsboro'), ('Wisner', 'Wisner'), ('Woodworth', 'Woodworth'), ('Youngsville', 'Youngsville'), ('Zachary', 'Zachary'), ('Zwolle', 'Zwolle'), ('Other', 'Other')], default='New Orleans', max_length=30),
        ),
        migrations.AlterField(
            model_name='student',
            name='city',
            field=models.CharField(choices=[('Abbeville', 'Abbeville'), ('Abita Springs', 'Abita Springs'), ('Addis', 'Addis'), ('Albany', 'Albany'), ('Alexandria', 'Alexandria'), ('Amite', 'Amite'), ('Anacoco', 'Anacoco'), ('Angie', 'Angie'), ('Arcadia', 'Arcadia'), ('Arnaudville', 'Arnaudville'), ('Ashland', 'Ashland'), ('Athens', 'Athens'), ('Atlanta', 'Atlanta'), ('Baker', 'Baker'), ('Baldwin', 'Baldwin'), ('Ball', 'Ball'), ('Basile', 'Basile'), ('Baskin', 'Baskin'), ('Bastrop', 'Bastrop'), ('Baton Rouge', 'Baton Rouge'), ('Belcher', 'Belcher'), ('Benton', 'Benton'), ('Bernice', 'Bernice'), ('Berwick', 'Berwick'), ('Bienville', 'Bienville'), ('Blanchard', 'Blanchard'), ('Bogalusa', 'Bogalusa'), ('Bonita', 'Bonita'), ('Bossier', 'Bossier'), ('Boutte', 'Boutte'), ('Boyce', 'Boyce'), ('Breaux Bridge', 'Breaux Bridge'), ('Broussard', 'Broussard'), ('Brusly', 'Brusly'), ('Bryceland', 'Bryceland'), ('Bunkie', 'Bunkie'), ('Calvin', 'Calvin'), ('Campti', 'Campti'), ('Cankton', 'Cankton'), ('Carencro', 'Carencro'), ('Castor', 'Castor'), ('Chalmette', 'Chalmette'), ('Central', 'Central'), ('Chataignier', 'Chataignier'), ('Chatham', 'Chatham'), ('Cheneyville', 'Cheneyville'), ('Choudrant', 'Choudrant'), ('Church Point', 'Church Point'), ('Clarence', 'Clarence'), ('Clarks', 'Clarks'), ('Clayton', 'Clayton'), ('Clinton', 'Clinton'), ('Colfax', 'Colfax'), ('Collinston', 'Collinston'), ('Columbia', 'Columbia'), ('Converse', 'Converse'), ('Cottonport', 'Cottonport'), ('Cotton Valley', 'Cotton Valley'), ('Coushatta', 'Coushatta'), ('Covington', 'Covington'), ('Creola', 'Creola'), ('Crowley', 'Crowley'), ('Cullen', 'Cullen'), ('Delcambre', 'Delcambre'), ('Delhi', 'Delhi'), ('Delta', 'Delta'), ('Denham Springs', 'Denham Springs'), ('DeQuincy', 'DeQuincy'), ('DeRidder', 'DeRidder'), ('Dixie Inn', 'Dixie Inn'), ('Dodson', 'Dodson'), ('Donaldsonville', 'Donaldsonville'), ('Downsville', 'Downsville'), ('Doyline', 'Doyline'), ('Dry Prong', 'Dry Prong'), ('Dubach', 'Dubach'), ('Dubberly', 'Dubberly'), ('Duson', 'Duson'), ('East Hodge', 'East Hodge'), ('Edgefield', 'Edgefield'), ('Elizabeth', 'Elizabeth'), ('Elton', 'Elton'), ('Epps', 'Epps'), ('Erath', 'Erath'), ('Eros', 'Eros'), ('Estherwood', 'Estherwood'), ('Eunice', 'Eunice'), ('Evergreen', 'Evergreen'), ('Farmerville', 'Farmerville'), ('Fenton', 'Fenton'), ('Ferriday', 'Ferriday'), ('Fisher', 'Fisher'), ('Florien', 'Florien'), ('Folsom', 'Folsom'), ('Fordoche', 'Fordoche'), ('Forest', 'Forest'), ('Forest Hill', 'Forest Hill'), ('Franklin', 'Franklin'), ('Franklinton', 'Franklinton'), ('French Settlement', 'French Settlement'), ('Georgetown', 'Georgetown'), ('Gibsland', 'Gibsland'), ('Gilbert', 'Gilbert'), ('Gilliam', 'Gilliam'), ('Glenmora', 'Glenmora'), ('Golden Meadow', 'Golden Meadow'), ('Goldonna', 'Goldonna'), ('Gonzales', 'Gonzales'), ('Grambling', 'Grambling'), ('Gramercy', 'Gramercy'), ('Grand Cane', 'Grand Cane'), ('Grand Coteau', 'Grand Coteau'), ('Grand Isle', 'Grand Isle'), ('Grayson', 'Grayson'), ('Greensburg', 'Greensburg'), ('Greenwood', 'Greenwood'), ('Gretna', 'Gretna'), ('Grosse Tete', 'Grosse Tete'), ('Gueydan', 'Gueydan'), ('Hall Summit', 'Hall Summit'), ('Hammond', 'Hammond'), ('Harahan', 'Harahan'), ('Harrisonburg', 'Harrisonburg'), ('Haughton', 'Haughton'), ('Haynesville', 'Haynesville'), ('Heflin', 'Heflin'), ('Henderson', 'Henderson'), ('Hessmer', 'Hessmer'), ('Hodge', 'Hodge'), ('Homer', 'Homer'), ('Hornbeck', 'Hornbeck'), ('Hosston', 'Hosston'), ('Houma', 'Houma'), ('Ida', 'Ida'), ('Independence', 'Independence'), ('Iota', 'Iota'), ('Iowa', 'Iowa'), ('Jackson', 'Jackson'), ('Jamestown', 'Jamestown'), ('Jeanerette', 'Jeanerette'), ('Jean Lafitte', 'Jean Lafitte'), ('Jena', 'Jena'), ('Jennings', 'Jennings'), ('Jonesboro', 'Jonesboro'), ('Jonesville', 'Jonesville'), ('Junction', 'Junction'), ('Kaplan', 'Kaplan'), ('Keachi', 'Keachi'), ('Keithville', 'Keithville'), ('Kenner', 'Kenner'), ('Kentwood', 'Kentwood'), ('Kilbourne', 'Kilbourne'), ('Killian', 'Killian'), ('Kinder', 'Kinder'), ('Krotz Springs', 'Krotz Springs'), ('Lafayette', 'Lafayette'), ('Lake Arthur', 'Lake Arthur'), ('Lake Charles', 'Lake Charles'), ('Lake Providence', 'Lake Providence'), ('Lecompte', 'Lecompte'), ('Leesville', 'Leesville'), ('Leonville', 'Leonville'), ('Lillie', 'Lillie'), ('Lisbon', 'Lisbon'), ('Livingston', 'Livingston'), ('Livonia', 'Livonia'), ('Lockport', 'Lockport'), ('Logansport', 'Logansport'), ('Longstreet', 'Longstreet'), ('Loreauville', 'Loreauville'), ('Lucky', 'Lucky'), ('Lutcher', 'Lutcher'), ('McNary', 'McNary'), ('Madisonville', 'Madisonville'), ('Mamou', 'Mamou'), ('Mandeville', 'Mandeville'), ('Mangham', 'Mangham'), ('Mansfield', 'Mansfield'), ('Mansura', 'Mansura'), ('Many', 'Many'), ('Maringouin', 'Maringouin'), ('Marion', 'Marion'), ('Marksville', 'Marksville'), ('Martin', 'Martin'), ('Maurice', 'Maurice'), ('Melville', 'Melville'), ('Mermentau', 'Mermentau'), ('Mer Rouge', 'Mer Rouge'), ('Merryville', 'Merryville'), ('Metairie', 'Metairie'), ('Minden', 'Minden'), ('Monroe', 'Monroe'), ('Montgomery', 'Montgomery'), ('Montpelier', 'Montpelier'), ('Mooringsport', 'Mooringsport'), ('Moreauville', 'Moreauville'), ('Morgan City', 'Morgan City'), ('Morganza', 'Morganza'), ('Morse', 'Morse'), ('Mound', 'Mound'), ('Mount Lebanon', 'Mount Lebanon'), ('Napoleonville', 'Napoleonville'), ('Natchez', 'Natchez'), ('Natchitoches', 'Natchitoches'), ('Newellton', 'Newellton'), ('New Iberia', 'New Iberia'), ('New Llano', 'New Llano'), ('New Orleans', 'New Orleans'), ('New Roads', 'New Roads'), ('Noble', 'Noble'), ('North Hodge', 'North Hodge'), ('Norwood', 'Norwood'), ('Oakdale', 'Oakdale'), ('Oak Grove', 'Oak Grove'), ('Oak Ridge', 'Oak Ridge'), ('Oberlin', 'Oberlin'), ('Oil City', 'Oil City'), ('Olla', 'Olla'), ('Opelousas', 'Opelousas'), ('Palmetto', 'Palmetto'), ('Parks', 'Parks'), ('Patterson', 'Patterson'), ('Pearl River', 'Pearl River'), ('Pine Prairie', 'Pine Prairie'), ('Pineville', 'Pineville'), ('Pioneer', 'Pioneer'), ('Plain Dealing', 'Plain Dealing'), ('Plaquemine', 'Plaquemine'), ('Plaucheville', 'Plaucheville'), ('Pleasant Hill', 'Pleasant Hill'), ('Pollock', 'Pollock'), ('Ponchatoula', 'Ponchatoula'), ('Port Allen', 'Port Allen'), ('Port Barre', 'Port Barre'), ('Port Vincent', 'Port Vincent'), ('Powhatan', 'Powhatan'), ('Provencal', 'Provencal'), ('Quitman', 'Quitman'), ('Rayne', 'Rayne'), ('Rayville', 'Rayville'), ('Reeves', 'Reeves'), ('Richmond', 'Richmond'), ('Richwood', 'Richwood'), ('Ridgecrest', 'Ridgecrest'), ('Ringgold', 'Ringgold'), ('Robeline', 'Robeline'), ('Rodessa', 'Rodessa'), ('Rosedale', 'Rosedale'), ('Roseland', 'Roseland'), ('Rosepine', 'Rosepine'), ('Ruston', 'Ruston'), ('St. Francisville', 'St. Francisville'), ('St. Gabriel', 'St. Gabriel'), ('St. Joseph', 'St. Joseph'), ('St. Martinville', 'St. Martinville'), ('Saline', 'Saline'), ('Sarepta', 'Sarepta'), ('Scott', 'Scott'), ('Shongaloo', 'Shongaloo'), ('Shreveport', 'Shreveport'), ('Sibley', 'Sibley'), ('Sicily Island', 'Sicily Island'), ('Sikes', 'Sikes'), ('Simmesport', 'Simmesport'), ('Simpson', 'Simpson'), ('Simsboro', 'Simsboro'), ('Slaughter', 'Slaughter'), ('Slidell', 'Slidell'), ('Sorrento', 'Sorrento'), ('South Mansfield', 'South Mansfield'), ('Spearsville', 'Spearsville'), ('Springfield', 'Springfield'), ('Springhill', 'Springhill'), ('Stanley', 'Stanley'), ('Sterlington', 'Sterlington'), ('Stonewall', 'Stonewall'), ('Sulphur', 'Sulphur'), ('Sun', 'Sun'), ('Sunset', 'Sunset'), ('Tallulah', 'Tallulah'), ('Tangipahoa', 'Tangipahoa'), ('Thibodaux', 'Thibodaux'), ('Tickfaw', 'Tickfaw'), ('Tullos', 'Tullos'), ('Turkey Creek', 'Turkey Creek'), ('Urania', 'Urania'), ('Varnado', 'Varnado'), ('Vidalia', 'Vidalia'), ('Vienna', 'Vienna'), ('Ville Platte', 'Ville Platte'), ('Vinton', 'Vinton'), ('Vivian', 'Vivian'), ('Walker', 'Walker'), ('Washington', 'Washington'), ('Waterproof', 'Waterproof'), ('Welsh', 'Welsh'), ('Westlake', 'Westlake'), ('West Monroe', 'West Monroe'), ('Westwego', 'Westwego'), ('White Castle', 'White Castle'), ('Wilson', 'Wilson'), ('Winnfield', 'Winnfield'), ('Winnsboro', 'Winnsboro'), ('Wisner', 'Wisner'), ('Woodworth', 'Woodworth'), ('Youngsville', 'Youngsville'), ('Zachary', 'Zachary'), ('Zwolle', 'Zwolle'), ('Other', 'Other')], default='New Orleans', max_length=30),
        ),
    ]
