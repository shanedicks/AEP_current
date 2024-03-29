# Generated by Django 4.0.4 on 2022-08-26 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0078_auto_20220201_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='other_city',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='student',
            name='afternoon',
            field=models.BooleanField(default=False, verbose_name='Afternoon'),
        ),
        migrations.AddField(
            model_name='student',
            name='allow_texts',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_1',
            field=models.BooleanField(default=False, verbose_name='I want to earn a high school equivalency diploma (HiSET, formerly GED)'),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_2',
            field=models.BooleanField(default=False, verbose_name='I want to work on my reading, writing, or math skills'),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_3',
            field=models.BooleanField(default=False, verbose_name='I want to learn English'),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_4',
            field=models.BooleanField(default=False, verbose_name='I want to prepare for college'),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_5',
            field=models.BooleanField(default=False, verbose_name='I want to work on my computer skills, financial skills, or health literacy'),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_6',
            field=models.BooleanField(default=False, verbose_name='I want to start college classes while working on my reading, writing, and math skills'),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_7',
            field=models.BooleanField(default=False, verbose_name='I want to participate in workforce trainings wille working on my reading, writing, and math skills'),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_8',
            field=models.BooleanField(default=False, verbose_name='I want to start college classes while earning my high school equivalency diploma'),
        ),
        migrations.AddField(
            model_name='student',
            name='check_goal_9',
            field=models.BooleanField(default=False, verbose_name='I want to explore career options'),
        ),
        migrations.AddField(
            model_name='student',
            name='computer_access',
            field=models.BooleanField(default=False, verbose_name='I have access to a computer or device to participate in online classes or resources'),
        ),
        migrations.AddField(
            model_name='student',
            name='evening',
            field=models.BooleanField(default=False, verbose_name='Evening'),
        ),
        migrations.AddField(
            model_name='student',
            name='hybrid',
            field=models.BooleanField(default=False, verbose_name='Hybrid - some online and some in person'),
        ),
        migrations.AddField(
            model_name='student',
            name='internet_access',
            field=models.BooleanField(default=False, verbose_name='I have access to the internet'),
        ),
        migrations.AddField(
            model_name='student',
            name='morning',
            field=models.BooleanField(default=False, verbose_name='Morning'),
        ),
        migrations.AddField(
            model_name='student',
            name='on_campus',
            field=models.BooleanField(default=False, verbose_name='On Campus - in person courses where students meet at a specific time as a group'),
        ),
        migrations.AddField(
            model_name='student',
            name='online_cohort',
            field=models.BooleanField(default=False, verbose_name='Online, Cohort - online course where students meet at a specific time as a group'),
        ),
        migrations.AddField(
            model_name='student',
            name='online_solo',
            field=models.BooleanField(default=False, verbose_name='Online, Self Paced - online coursework completed when learner is ready'),
        ),
        migrations.AddField(
            model_name='student',
            name='other_city',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='student',
            name='primary_goal',
            field=models.CharField(choices=[('1', 'I want to earn a high school equivalency diploma (HiSET, formerly GED)'), ('2', 'I want to work on my reading, writing, or math skills'), ('3', 'I want to learn English'), ('4', 'I want to prepare for college'), ('5', 'I want to work on my computer skills, financial skills, or health literacy'), ('6', 'I want to start college classes while working on my reading, writing, and math skills'), ('7', 'I want to participate in workforce trainings wille working on my reading, writing, and math skills'), ('8', 'I want to start college classes while earning my high school equivalency diploma'), ('9', 'I want to explore career options')], default='1', max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='weekend',
            field=models.BooleanField(default=False, verbose_name='Weekend'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='SNAP',
            field=models.BooleanField(default=False, verbose_name='SNAP (Supplemental Nutrition Assistance Program) Food Stamps'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='SSI',
            field=models.BooleanField(default=False, verbose_name='SSI (Supplemental Security Income)'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='TANF',
            field=models.BooleanField(default=False, verbose_name='TANF (Temporary Assistance for Needy Families'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='TANF_2',
            field=models.BooleanField(default=False, verbose_name='Have you recieved TANF for more than two years in total?'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='Tstate',
            field=models.BooleanField(default=False, verbose_name='Tstate or Local income-based public assistance'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='criminal_record',
            field=models.BooleanField(default=False, verbose_name='I have a criminal record that makes it hard to find a job.'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='current_industry',
            field=models.CharField(blank=True, max_length=100, verbose_name='If you are currently employed, what industry cluster do you work in?'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='digital_signature',
            field=models.CharField(blank=True, max_length=100, verbose_name='DISCLAIMER: By typing your name below, you are signing this application electronically. You agree that your electronic signature is the legal equivalent of your manual signature on this application.'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_notice',
            field=models.CharField(blank=True, choices=[('1', 'Yes'), ('2', 'No'), ('3', 'Do not wish to disclose')], help_text='In the Americans with Disabilities Act of 1990, a disability is defined as a physical or mental impairment that substantially limits one or more of a person’s major life activities.', max_length=1, verbose_name='Are you an Individual with a Disability?'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='foster_care',
            field=models.BooleanField(default=False, verbose_name='I am in the foster care system (or used to be) and I am less than 24 years old.'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='help_with_schoolwork',
            field=models.BooleanField(default=False, verbose_name='Helping more frequently with their schoolwork.'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='household_income',
            field=models.PositiveIntegerField(default=0, verbose_name='Annual Household Income'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='household_size',
            field=models.PositiveIntegerField(default=1, verbose_name='How many family members including yourself have lived in your household in the past six months?'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='industry_preference',
            field=models.CharField(blank=True, max_length=100, verbose_name='If you could get a job or change jobs, what industry cluster would you like to work in?'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='other_country',
            field=models.CharField(blank=True, max_length=20, verbose_name='Other Country if not listed'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='other_language',
            field=models.CharField(blank=True, max_length=20, verbose_name='Other Native Language Not Listed'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='parent_volunteering',
            field=models.BooleanField(default=False, verbose_name="Being more involved in my children's school, such as attendending school activities and parent meetings, and volunteering"),
        ),
        migrations.AddField(
            model_name='wioa',
            name='parental_status',
            field=models.CharField(blank=True, choices=[('1', 'parent of children 1-5'), ('2', 'parent of children 6-10'), ('3', 'parent of children 11-13'), ('4', 'parent of children 14-18'), ('0', 'No')], max_length=2, verbose_name='Are you a parent?'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='purchase_books',
            field=models.BooleanField(default=False, verbose_name='Purchasing books or magazines'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='read_to_children',
            field=models.BooleanField(default=False, verbose_name='Reading to children'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='referred_by',
            field=models.CharField(blank=True, choices=[('1', 'TV'), ('2', 'RADIO'), ('3', 'SOCIAL MEDIA'), ('4', 'BROCHURE'), ('5', 'CAREER COMPASS'), ('6', 'COACH'), ('7', 'COLLEGE RECRUITER'), ('8', 'FACULTY/STAFF'), ('9', 'FAMILY MEMBER'), ('10', 'FORMER STUDENT'), ('11', 'FRIEND'), ('12', 'HIGH SCHOOL COUNSELOR'), ('13', 'INTERNET SEARCH'), ('14', 'NEWSPAPER'), ('15', 'OTHER'), ('16', 'ONE STOP'), ('17', 'AMERICAN JOB CENTER'), ('18', 'UNEMPLOYMENT OFFICE')], max_length=2),
        ),
        migrations.AddField(
            model_name='wioa',
            name='request_accommodation',
            field=models.BooleanField(default=False, help_text='If you have a disability and/or a condition for which you would like special accommodations for instruction or testing it is your responsibility to notify the program’s administrative office and provide professional documentation.', verbose_name='Check here to indicate that you understand your responsibility to request accommodations.'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='student_teacher_contact',
            field=models.BooleanField(default=False, verbose_name="Increasing contact with my children's teachers to discuss children's education"),
        ),
        migrations.AddField(
            model_name='wioa',
            name='veteran',
            field=models.BooleanField(default=False, verbose_name='I am a veteran'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='visit_library',
            field=models.BooleanField(default=False, verbose_name='Visiting a library'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='city',
            field=models.CharField(choices=[('Abbeville', 'Abbeville'), ('Abita Springs', 'Abita Springs'), ('Addis', 'Addis'), ('Albany', 'Albany'), ('Alexandria', 'Alexandria'), ('Amite', 'Amite'), ('Anacoco', 'Anacoco'), ('Angie', 'Angie'), ('Arcadia', 'Arcadia'), ('Arnaudville', 'Arnaudville'), ('Ashland', 'Ashland'), ('Athens', 'Athens'), ('Atlanta', 'Atlanta'), ('Baker', 'Baker'), ('Baldwin', 'Baldwin'), ('Ball', 'Ball'), ('Basile', 'Basile'), ('Baskin', 'Baskin'), ('Bastrop', 'Bastrop'), ('Baton Rouge', 'Baton Rouge'), ('Belcher', 'Belcher'), ('Benton', 'Benton'), ('Bernice', 'Bernice'), ('Berwick', 'Berwick'), ('Bienville', 'Bienville'), ('Blanchard', 'Blanchard'), ('Bogalusa', 'Bogalusa'), ('Bonita', 'Bonita'), ('Bossier', 'Bossier'), ('Boyce', 'Boyce'), ('Breaux Bridge', 'Breaux Bridge'), ('Broussard', 'Broussard'), ('Brusly', 'Brusly'), ('Bryceland', 'Bryceland'), ('Bunkie', 'Bunkie'), ('Calvin', 'Calvin'), ('Campti', 'Campti'), ('Cankton', 'Cankton'), ('Carencro', 'Carencro'), ('Castor', 'Castor'), ('Central', 'Central'), ('Chataignier', 'Chataignier'), ('Chatham', 'Chatham'), ('Cheneyville', 'Cheneyville'), ('Choudrant', 'Choudrant'), ('Church Point', 'Church Point'), ('Clarence', 'Clarence'), ('Clarks', 'Clarks'), ('Clayton', 'Clayton'), ('Clinton', 'Clinton'), ('Colfax', 'Colfax'), ('Collinston', 'Collinston'), ('Columbia', 'Columbia'), ('Converse', 'Converse'), ('Cottonport', 'Cottonport'), ('Cotton Valley', 'Cotton Valley'), ('Coushatta', 'Coushatta'), ('Covington', 'Covington'), ('Creola', 'Creola'), ('Crowley', 'Crowley'), ('Cullen', 'Cullen'), ('Delcambre', 'Delcambre'), ('Delhi', 'Delhi'), ('Delta', 'Delta'), ('Denham Springs', 'Denham Springs'), ('DeQuincy', 'DeQuincy'), ('DeRidder', 'DeRidder'), ('Dixie Inn', 'Dixie Inn'), ('Dodson', 'Dodson'), ('Donaldsonville', 'Donaldsonville'), ('Downsville', 'Downsville'), ('Doyline', 'Doyline'), ('Dry Prong', 'Dry Prong'), ('Dubach', 'Dubach'), ('Dubberly', 'Dubberly'), ('Duson', 'Duson'), ('East Hodge', 'East Hodge'), ('Edgefield', 'Edgefield'), ('Elizabeth', 'Elizabeth'), ('Elton', 'Elton'), ('Epps', 'Epps'), ('Erath', 'Erath'), ('Eros', 'Eros'), ('Estherwood', 'Estherwood'), ('Eunice', 'Eunice'), ('Evergreen', 'Evergreen'), ('Farmerville', 'Farmerville'), ('Fenton', 'Fenton'), ('Ferriday', 'Ferriday'), ('Fisher', 'Fisher'), ('Florien', 'Florien'), ('Folsom', 'Folsom'), ('Fordoche', 'Fordoche'), ('Forest', 'Forest'), ('Forest Hill', 'Forest Hill'), ('Franklin', 'Franklin'), ('Franklinton', 'Franklinton'), ('French Settlement', 'French Settlement'), ('Georgetown', 'Georgetown'), ('Gibsland', 'Gibsland'), ('Gilbert', 'Gilbert'), ('Gilliam', 'Gilliam'), ('Glenmora', 'Glenmora'), ('Golden Meadow', 'Golden Meadow'), ('Goldonna', 'Goldonna'), ('Gonzales', 'Gonzales'), ('Grambling', 'Grambling'), ('Gramercy', 'Gramercy'), ('Grand Cane', 'Grand Cane'), ('Grand Coteau', 'Grand Coteau'), ('Grand Isle', 'Grand Isle'), ('Grayson', 'Grayson'), ('Greensburg', 'Greensburg'), ('Greenwood', 'Greenwood'), ('Gretna', 'Gretna'), ('Grosse Tete', 'Grosse Tete'), ('Gueydan', 'Gueydan'), ('Hall Summit', 'Hall Summit'), ('Hammond', 'Hammond'), ('Harahan', 'Harahan'), ('Harrisonburg', 'Harrisonburg'), ('Haughton', 'Haughton'), ('Haynesville', 'Haynesville'), ('Heflin', 'Heflin'), ('Henderson', 'Henderson'), ('Hessmer', 'Hessmer'), ('Hodge', 'Hodge'), ('Homer', 'Homer'), ('Hornbeck', 'Hornbeck'), ('Hosston', 'Hosston'), ('Houma', 'Houma'), ('Ida', 'Ida'), ('Independence', 'Independence'), ('Iota', 'Iota'), ('Iowa', 'Iowa'), ('Jackson', 'Jackson'), ('Jamestown', 'Jamestown'), ('Jeanerette', 'Jeanerette'), ('Jean Lafitte', 'Jean Lafitte'), ('Jena', 'Jena'), ('Jennings', 'Jennings'), ('Jonesboro', 'Jonesboro'), ('Jonesville', 'Jonesville'), ('Junction', 'Junction'), ('Kaplan', 'Kaplan'), ('Keachi', 'Keachi'), ('Keithville', 'Keithville'), ('Kenner', 'Kenner'), ('Kentwood', 'Kentwood'), ('Kilbourne', 'Kilbourne'), ('Killian', 'Killian'), ('Kinder', 'Kinder'), ('Krotz Springs', 'Krotz Springs'), ('Lafayette', 'Lafayette'), ('Lake Arthur', 'Lake Arthur'), ('Lake Charles', 'Lake Charles'), ('Lake Providence', 'Lake Providence'), ('Lecompte', 'Lecompte'), ('Leesville', 'Leesville'), ('Leonville', 'Leonville'), ('Lillie', 'Lillie'), ('Lisbon', 'Lisbon'), ('Livingston', 'Livingston'), ('Livonia', 'Livonia'), ('Lockport', 'Lockport'), ('Logansport', 'Logansport'), ('Longstreet', 'Longstreet'), ('Loreauville', 'Loreauville'), ('Lucky', 'Lucky'), ('Lutcher', 'Lutcher'), ('McNary', 'McNary'), ('Madisonville', 'Madisonville'), ('Mamou', 'Mamou'), ('Mandeville', 'Mandeville'), ('Mangham', 'Mangham'), ('Mansfield', 'Mansfield'), ('Mansura', 'Mansura'), ('Many', 'Many'), ('Maringouin', 'Maringouin'), ('Marion', 'Marion'), ('Marksville', 'Marksville'), ('Martin', 'Martin'), ('Maurice', 'Maurice'), ('Melville', 'Melville'), ('Mermentau', 'Mermentau'), ('Mer Rouge', 'Mer Rouge'), ('Merryville', 'Merryville'), ('Minden', 'Minden'), ('Monroe', 'Monroe'), ('Montgomery', 'Montgomery'), ('Montpelier', 'Montpelier'), ('Mooringsport', 'Mooringsport'), ('Moreauville', 'Moreauville'), ('Morgan', 'Morgan'), ('Morganza', 'Morganza'), ('Morse', 'Morse'), ('Mound', 'Mound'), ('Mount Lebanon', 'Mount Lebanon'), ('Napoleonville', 'Napoleonville'), ('Natchez', 'Natchez'), ('Natchitoches', 'Natchitoches'), ('Newellton', 'Newellton'), ('New Iberia', 'New Iberia'), ('New Llano', 'New Llano'), ('New Orleans', 'New Orleans'), ('New Roads', 'New Roads'), ('Noble', 'Noble'), ('North Hodge', 'North Hodge'), ('Norwood', 'Norwood'), ('Oakdale', 'Oakdale'), ('Oak Grove', 'Oak Grove'), ('Oak Ridge', 'Oak Ridge'), ('Oberlin', 'Oberlin'), ('Oil', 'Oil'), ('Olla', 'Olla'), ('Opelousas', 'Opelousas'), ('Palmetto', 'Palmetto'), ('Parks', 'Parks'), ('Patterson', 'Patterson'), ('Pearl River', 'Pearl River'), ('Pine Prairie', 'Pine Prairie'), ('Pineville', 'Pineville'), ('Pioneer', 'Pioneer'), ('Plain Dealing', 'Plain Dealing'), ('Plaquemine', 'Plaquemine'), ('Plaucheville', 'Plaucheville'), ('Pleasant Hill', 'Pleasant Hill'), ('Pollock', 'Pollock'), ('Ponchatoula', 'Ponchatoula'), ('Port Allen', 'Port Allen'), ('Port Barre', 'Port Barre'), ('Port Vincent', 'Port Vincent'), ('Powhatan', 'Powhatan'), ('Provencal', 'Provencal'), ('Quitman', 'Quitman'), ('Rayne', 'Rayne'), ('Rayville', 'Rayville'), ('Reeves', 'Reeves'), ('Richmond', 'Richmond'), ('Richwood', 'Richwood'), ('Ridgecrest', 'Ridgecrest'), ('Ringgold', 'Ringgold'), ('Robeline', 'Robeline'), ('Rodessa', 'Rodessa'), ('Rosedale', 'Rosedale'), ('Roseland', 'Roseland'), ('Rosepine', 'Rosepine'), ('Ruston', 'Ruston'), ('St. Francisville', 'St. Francisville'), ('St. Gabriel', 'St. Gabriel'), ('St. Joseph', 'St. Joseph'), ('St. Martinville', 'St. Martinville'), ('Saline', 'Saline'), ('Sarepta', 'Sarepta'), ('Scott', 'Scott'), ('Shongaloo', 'Shongaloo'), ('Shreveport', 'Shreveport'), ('Sibley', 'Sibley'), ('Sicily Island', 'Sicily Island'), ('Sikes', 'Sikes'), ('Simmesport', 'Simmesport'), ('Simpson', 'Simpson'), ('Simsboro', 'Simsboro'), ('Slaughter', 'Slaughter'), ('Slidell', 'Slidell'), ('Sorrento', 'Sorrento'), ('South Mansfield', 'South Mansfield'), ('Spearsville', 'Spearsville'), ('Springfield', 'Springfield'), ('Springhill', 'Springhill'), ('Stanley', 'Stanley'), ('Sterlington', 'Sterlington'), ('Stonewall', 'Stonewall'), ('Sulphur', 'Sulphur'), ('Sun', 'Sun'), ('Sunset', 'Sunset'), ('Tallulah', 'Tallulah'), ('Tangipahoa', 'Tangipahoa'), ('Thibodaux', 'Thibodaux'), ('Tickfaw', 'Tickfaw'), ('Tullos', 'Tullos'), ('Turkey Creek', 'Turkey Creek'), ('Urania', 'Urania'), ('Varnado', 'Varnado'), ('Vidalia', 'Vidalia'), ('Vienna', 'Vienna'), ('Ville Platte', 'Ville Platte'), ('Vinton', 'Vinton'), ('Vivian', 'Vivian'), ('Walker', 'Walker'), ('Washington', 'Washington'), ('Waterproof', 'Waterproof'), ('Welsh', 'Welsh'), ('Westlake', 'Westlake'), ('West Monroe', 'West Monroe'), ('Westwego', 'Westwego'), ('White Castle', 'White Castle'), ('Wilson', 'Wilson'), ('Winnfield', 'Winnfield'), ('Winnsboro', 'Winnsboro'), ('Wisner', 'Wisner'), ('Woodworth', 'Woodworth'), ('Youngsville', 'Youngsville'), ('Zachary', 'Zachary'), ('Zwolle', 'Zwolle'), ('Other', 'Other')], max_length=30),
        ),
        migrations.AlterField(
            model_name='student',
            name='city',
            field=models.CharField(choices=[('Abbeville', 'Abbeville'), ('Abita Springs', 'Abita Springs'), ('Addis', 'Addis'), ('Albany', 'Albany'), ('Alexandria', 'Alexandria'), ('Amite', 'Amite'), ('Anacoco', 'Anacoco'), ('Angie', 'Angie'), ('Arcadia', 'Arcadia'), ('Arnaudville', 'Arnaudville'), ('Ashland', 'Ashland'), ('Athens', 'Athens'), ('Atlanta', 'Atlanta'), ('Baker', 'Baker'), ('Baldwin', 'Baldwin'), ('Ball', 'Ball'), ('Basile', 'Basile'), ('Baskin', 'Baskin'), ('Bastrop', 'Bastrop'), ('Baton Rouge', 'Baton Rouge'), ('Belcher', 'Belcher'), ('Benton', 'Benton'), ('Bernice', 'Bernice'), ('Berwick', 'Berwick'), ('Bienville', 'Bienville'), ('Blanchard', 'Blanchard'), ('Bogalusa', 'Bogalusa'), ('Bonita', 'Bonita'), ('Bossier', 'Bossier'), ('Boyce', 'Boyce'), ('Breaux Bridge', 'Breaux Bridge'), ('Broussard', 'Broussard'), ('Brusly', 'Brusly'), ('Bryceland', 'Bryceland'), ('Bunkie', 'Bunkie'), ('Calvin', 'Calvin'), ('Campti', 'Campti'), ('Cankton', 'Cankton'), ('Carencro', 'Carencro'), ('Castor', 'Castor'), ('Central', 'Central'), ('Chataignier', 'Chataignier'), ('Chatham', 'Chatham'), ('Cheneyville', 'Cheneyville'), ('Choudrant', 'Choudrant'), ('Church Point', 'Church Point'), ('Clarence', 'Clarence'), ('Clarks', 'Clarks'), ('Clayton', 'Clayton'), ('Clinton', 'Clinton'), ('Colfax', 'Colfax'), ('Collinston', 'Collinston'), ('Columbia', 'Columbia'), ('Converse', 'Converse'), ('Cottonport', 'Cottonport'), ('Cotton Valley', 'Cotton Valley'), ('Coushatta', 'Coushatta'), ('Covington', 'Covington'), ('Creola', 'Creola'), ('Crowley', 'Crowley'), ('Cullen', 'Cullen'), ('Delcambre', 'Delcambre'), ('Delhi', 'Delhi'), ('Delta', 'Delta'), ('Denham Springs', 'Denham Springs'), ('DeQuincy', 'DeQuincy'), ('DeRidder', 'DeRidder'), ('Dixie Inn', 'Dixie Inn'), ('Dodson', 'Dodson'), ('Donaldsonville', 'Donaldsonville'), ('Downsville', 'Downsville'), ('Doyline', 'Doyline'), ('Dry Prong', 'Dry Prong'), ('Dubach', 'Dubach'), ('Dubberly', 'Dubberly'), ('Duson', 'Duson'), ('East Hodge', 'East Hodge'), ('Edgefield', 'Edgefield'), ('Elizabeth', 'Elizabeth'), ('Elton', 'Elton'), ('Epps', 'Epps'), ('Erath', 'Erath'), ('Eros', 'Eros'), ('Estherwood', 'Estherwood'), ('Eunice', 'Eunice'), ('Evergreen', 'Evergreen'), ('Farmerville', 'Farmerville'), ('Fenton', 'Fenton'), ('Ferriday', 'Ferriday'), ('Fisher', 'Fisher'), ('Florien', 'Florien'), ('Folsom', 'Folsom'), ('Fordoche', 'Fordoche'), ('Forest', 'Forest'), ('Forest Hill', 'Forest Hill'), ('Franklin', 'Franklin'), ('Franklinton', 'Franklinton'), ('French Settlement', 'French Settlement'), ('Georgetown', 'Georgetown'), ('Gibsland', 'Gibsland'), ('Gilbert', 'Gilbert'), ('Gilliam', 'Gilliam'), ('Glenmora', 'Glenmora'), ('Golden Meadow', 'Golden Meadow'), ('Goldonna', 'Goldonna'), ('Gonzales', 'Gonzales'), ('Grambling', 'Grambling'), ('Gramercy', 'Gramercy'), ('Grand Cane', 'Grand Cane'), ('Grand Coteau', 'Grand Coteau'), ('Grand Isle', 'Grand Isle'), ('Grayson', 'Grayson'), ('Greensburg', 'Greensburg'), ('Greenwood', 'Greenwood'), ('Gretna', 'Gretna'), ('Grosse Tete', 'Grosse Tete'), ('Gueydan', 'Gueydan'), ('Hall Summit', 'Hall Summit'), ('Hammond', 'Hammond'), ('Harahan', 'Harahan'), ('Harrisonburg', 'Harrisonburg'), ('Haughton', 'Haughton'), ('Haynesville', 'Haynesville'), ('Heflin', 'Heflin'), ('Henderson', 'Henderson'), ('Hessmer', 'Hessmer'), ('Hodge', 'Hodge'), ('Homer', 'Homer'), ('Hornbeck', 'Hornbeck'), ('Hosston', 'Hosston'), ('Houma', 'Houma'), ('Ida', 'Ida'), ('Independence', 'Independence'), ('Iota', 'Iota'), ('Iowa', 'Iowa'), ('Jackson', 'Jackson'), ('Jamestown', 'Jamestown'), ('Jeanerette', 'Jeanerette'), ('Jean Lafitte', 'Jean Lafitte'), ('Jena', 'Jena'), ('Jennings', 'Jennings'), ('Jonesboro', 'Jonesboro'), ('Jonesville', 'Jonesville'), ('Junction', 'Junction'), ('Kaplan', 'Kaplan'), ('Keachi', 'Keachi'), ('Keithville', 'Keithville'), ('Kenner', 'Kenner'), ('Kentwood', 'Kentwood'), ('Kilbourne', 'Kilbourne'), ('Killian', 'Killian'), ('Kinder', 'Kinder'), ('Krotz Springs', 'Krotz Springs'), ('Lafayette', 'Lafayette'), ('Lake Arthur', 'Lake Arthur'), ('Lake Charles', 'Lake Charles'), ('Lake Providence', 'Lake Providence'), ('Lecompte', 'Lecompte'), ('Leesville', 'Leesville'), ('Leonville', 'Leonville'), ('Lillie', 'Lillie'), ('Lisbon', 'Lisbon'), ('Livingston', 'Livingston'), ('Livonia', 'Livonia'), ('Lockport', 'Lockport'), ('Logansport', 'Logansport'), ('Longstreet', 'Longstreet'), ('Loreauville', 'Loreauville'), ('Lucky', 'Lucky'), ('Lutcher', 'Lutcher'), ('McNary', 'McNary'), ('Madisonville', 'Madisonville'), ('Mamou', 'Mamou'), ('Mandeville', 'Mandeville'), ('Mangham', 'Mangham'), ('Mansfield', 'Mansfield'), ('Mansura', 'Mansura'), ('Many', 'Many'), ('Maringouin', 'Maringouin'), ('Marion', 'Marion'), ('Marksville', 'Marksville'), ('Martin', 'Martin'), ('Maurice', 'Maurice'), ('Melville', 'Melville'), ('Mermentau', 'Mermentau'), ('Mer Rouge', 'Mer Rouge'), ('Merryville', 'Merryville'), ('Minden', 'Minden'), ('Monroe', 'Monroe'), ('Montgomery', 'Montgomery'), ('Montpelier', 'Montpelier'), ('Mooringsport', 'Mooringsport'), ('Moreauville', 'Moreauville'), ('Morgan', 'Morgan'), ('Morganza', 'Morganza'), ('Morse', 'Morse'), ('Mound', 'Mound'), ('Mount Lebanon', 'Mount Lebanon'), ('Napoleonville', 'Napoleonville'), ('Natchez', 'Natchez'), ('Natchitoches', 'Natchitoches'), ('Newellton', 'Newellton'), ('New Iberia', 'New Iberia'), ('New Llano', 'New Llano'), ('New Orleans', 'New Orleans'), ('New Roads', 'New Roads'), ('Noble', 'Noble'), ('North Hodge', 'North Hodge'), ('Norwood', 'Norwood'), ('Oakdale', 'Oakdale'), ('Oak Grove', 'Oak Grove'), ('Oak Ridge', 'Oak Ridge'), ('Oberlin', 'Oberlin'), ('Oil', 'Oil'), ('Olla', 'Olla'), ('Opelousas', 'Opelousas'), ('Palmetto', 'Palmetto'), ('Parks', 'Parks'), ('Patterson', 'Patterson'), ('Pearl River', 'Pearl River'), ('Pine Prairie', 'Pine Prairie'), ('Pineville', 'Pineville'), ('Pioneer', 'Pioneer'), ('Plain Dealing', 'Plain Dealing'), ('Plaquemine', 'Plaquemine'), ('Plaucheville', 'Plaucheville'), ('Pleasant Hill', 'Pleasant Hill'), ('Pollock', 'Pollock'), ('Ponchatoula', 'Ponchatoula'), ('Port Allen', 'Port Allen'), ('Port Barre', 'Port Barre'), ('Port Vincent', 'Port Vincent'), ('Powhatan', 'Powhatan'), ('Provencal', 'Provencal'), ('Quitman', 'Quitman'), ('Rayne', 'Rayne'), ('Rayville', 'Rayville'), ('Reeves', 'Reeves'), ('Richmond', 'Richmond'), ('Richwood', 'Richwood'), ('Ridgecrest', 'Ridgecrest'), ('Ringgold', 'Ringgold'), ('Robeline', 'Robeline'), ('Rodessa', 'Rodessa'), ('Rosedale', 'Rosedale'), ('Roseland', 'Roseland'), ('Rosepine', 'Rosepine'), ('Ruston', 'Ruston'), ('St. Francisville', 'St. Francisville'), ('St. Gabriel', 'St. Gabriel'), ('St. Joseph', 'St. Joseph'), ('St. Martinville', 'St. Martinville'), ('Saline', 'Saline'), ('Sarepta', 'Sarepta'), ('Scott', 'Scott'), ('Shongaloo', 'Shongaloo'), ('Shreveport', 'Shreveport'), ('Sibley', 'Sibley'), ('Sicily Island', 'Sicily Island'), ('Sikes', 'Sikes'), ('Simmesport', 'Simmesport'), ('Simpson', 'Simpson'), ('Simsboro', 'Simsboro'), ('Slaughter', 'Slaughter'), ('Slidell', 'Slidell'), ('Sorrento', 'Sorrento'), ('South Mansfield', 'South Mansfield'), ('Spearsville', 'Spearsville'), ('Springfield', 'Springfield'), ('Springhill', 'Springhill'), ('Stanley', 'Stanley'), ('Sterlington', 'Sterlington'), ('Stonewall', 'Stonewall'), ('Sulphur', 'Sulphur'), ('Sun', 'Sun'), ('Sunset', 'Sunset'), ('Tallulah', 'Tallulah'), ('Tangipahoa', 'Tangipahoa'), ('Thibodaux', 'Thibodaux'), ('Tickfaw', 'Tickfaw'), ('Tullos', 'Tullos'), ('Turkey Creek', 'Turkey Creek'), ('Urania', 'Urania'), ('Varnado', 'Varnado'), ('Vidalia', 'Vidalia'), ('Vienna', 'Vienna'), ('Ville Platte', 'Ville Platte'), ('Vinton', 'Vinton'), ('Vivian', 'Vivian'), ('Walker', 'Walker'), ('Washington', 'Washington'), ('Waterproof', 'Waterproof'), ('Welsh', 'Welsh'), ('Westlake', 'Westlake'), ('West Monroe', 'West Monroe'), ('Westwego', 'Westwego'), ('White Castle', 'White Castle'), ('Wilson', 'Wilson'), ('Winnfield', 'Winnfield'), ('Winnsboro', 'Winnsboro'), ('Wisner', 'Wisner'), ('Woodworth', 'Woodworth'), ('Youngsville', 'Youngsville'), ('Zachary', 'Zachary'), ('Zwolle', 'Zwolle'), ('Other', 'Other')], max_length=30),
        ),
        migrations.AlterField(
            model_name='wioa',
            name='country',
            field=models.CharField(blank=True, choices=[('1', 'United States'), ('2', 'India'), ('3', 'Australia'), ('4', 'Japan'), ('5', 'New'), ('6', 'Philippines'), ('7', 'Turkey'), ('8', 'Austria'), ('9', 'Belgium'), ('10', 'Denmark'), ('11', 'France'), ('12', 'Germany'), ('13', 'Italy'), ('14', 'Portugal'), ('15', 'Spain'), ('16', 'Sweden'), ('17', 'Argentina'), ('18', 'Brazil'), ('19', 'Russia'), ('20', 'South'), ('21', 'Egypt'), ('22', 'England'), ('23', 'Greece'), ('24', 'Singapore'), ('25', 'South'), ('26', 'Mexico'), ('27', 'Afghanistan'), ('28', 'Algeria'), ('29', 'Albania'), ('30', 'Aruba'), ('31', 'Bahamas'), ('32', 'North'), ('33', 'Canada'), ('34', 'China'), ('35', 'Georgia'), ('36', 'Hong'), ('37', 'Indonesia'), ('38', 'Iraq'), ('39', 'Israel'), ('40', 'Kuwait'), ('41', 'Korea'), ('42', 'Lebanon'), ('43', 'Malaysia'), ('44', 'Nigeria'), ('45', 'Norway'), ('46', 'Oman'), ('47', 'Pakistan'), ('48', 'Switzerland'), ('49', 'Thailand'), ('50', 'United'), ('51', 'United'), ('52', 'Switzerland'), ('53', 'Thailand'), ('100', 'Other')], max_length=20, verbose_name='Country of Birth'),
        ),
        migrations.AlterField(
            model_name='wioa',
            name='current_employment_status',
            field=models.CharField(choices=[('1', 'Employed - Full Time'), ('9', 'Employed - Part Time'), ('8', 'Unemployed - Looking for work'), ('4', 'Not in labor force/ Not available for work'), ('5', 'Employed, but recieved notice of termination or Military seperation is pending'), ('6', 'Not in labor force and/or not looking for work'), ('7', 'Retired')], default='2', max_length=2, verbose_name='What is your current employment status'),
        ),
        migrations.AlterField(
            model_name='wioa',
            name='displaced_homemaker',
            field=models.BooleanField(default=False, verbose_name='I am a former homemaker who is having trouble finding a job or a better job.'),
        ),
        migrations.AlterField(
            model_name='wioa',
            name='lacks_adequate_residence',
            field=models.BooleanField(default=False, verbose_name='I am homeless. I live in a motel, hotel, campground, transitional housing, or with another person because I lost my house or apartment'),
        ),
        migrations.AlterField(
            model_name='wioa',
            name='long_term_unemployed',
            field=models.BooleanField(default=False, help_text='If you are not working, has it been 27 weeks (6 months) or longer since you had a job?', verbose_name='Long-term Unemployed'),
        ),
        migrations.AlterField(
            model_name='wioa',
            name='migrant_seasonal_status',
            field=models.CharField(choices=[('0', 'I am a farmworker'), ('1', 'I am a seasonal farmworker who has worked the last 12 months in agriculture or farm fishing labor'), ('2', 'I am a seasonal farmworker with no permanent residence (migrant)'), ('3', 'I am a dependent of a farmworker'), ('4', 'None of these apply to me')], default='4', max_length=2, verbose_name='Farmworker Status'),
        ),
        migrations.AlterField(
            model_name='wioa',
            name='single_parent',
            field=models.BooleanField(default=False, verbose_name='I am a single parent. I am unmarried or seperated from my spouse and have primary responsibility for one or more dependent children under the age of 18, or I am a single, pregnant woman.'),
        ),
    ]
