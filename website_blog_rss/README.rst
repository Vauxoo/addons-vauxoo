Website Blog RSS
================

**This App lets you create a RSS feed on populated by the blog posts stored on
the database.**

This module creates two url to export the **Blog Posts** model, the post should
be enabled to **Published On website**

 - The follow url `/blog_rss.xml` export all post registered into the
   **Blog Posts** model
 - The follow url `/blog/<model('blog.blog'):blog>/rss.xml` export all post 
   registered into the **Blog Posts** model, belongs to the **Blog** gone
   through arguments of the url
