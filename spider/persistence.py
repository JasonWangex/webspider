import mysql.connector

conn = mysql.connector.connect(user='root', password='wjz@17948', database='zhihu_users', use_unicode=True)
cursor = conn.cursor()
cursor.excute(
    "INSERT INTO users(name, uid, hashId, gender, avatar, introduction, description, career, location, education, approval, thanks, collected, share) VALUE (%s, %s, %s, %d, %s, %s, %s, %s, %s, %s, %d, %d, %d, %d)")
