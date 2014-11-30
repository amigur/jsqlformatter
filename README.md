jsqlformatter
=============

Java sql formatter. It takes the String / StringBuffer expression on the input and generates nicely formatted SQL string. It can be easily embedded 
into any editor (Eclipse/NetBeans...) using Autokey or AutoHkey. It is recommended to define hotkey in Autokey/AutoHKey that triggers jsqlformatter script. Jsqlformatter takes the clipboard content as an input, process the it and stores result back to clipboard so that the formatted text can be simly pasted to the editor (Eclipse, Netbeans etc.)

Example:

INPUT:

```Java
sb.append(" select ");
sb.append(" home_url, ");
sb.append(" user_first_name ");
sb.append(" from ");
sb.append(User.TABLE);
sb.append(" WHERE ");
sb.append(" url LIKE '" + like + "' ");
sb.append(" and user_id != " + userId);
sb.append(" order by");
sb.append(" NLSSORT(user_first_name,'NLS_SORT=XWEST_EUROPEAN')");
```

OUTPUT:

```Java
	"SELECT " +
			"home_url,  user_first_name  " +
	"FROM " +
			User.TABLE + " " +
	"WHERE " +
			"url LIKE '" +  like + "'  " +
			"AND user_id != " +  userId + " " +
	"ORDER BY " +
			"NLSSORT(user_first_name, " +
			"'NLS_SORT=XWEST_EUROPEAN')";
```
