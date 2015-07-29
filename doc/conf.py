# -*- coding: utf-8 -*-

extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
]

#templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'urbs'
copyright = u'2014, tum-ens'
version = '0.4'
release = '0.4'

exclude_patterns = ['_build']
#pygments_style = 'sphinx'

# HTML output

htmlhelp_basename = 'urbsdoc'

# LaTeX output

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  ('index', 'urbs.tex', u'urbs Documentation',
   u'tum-ens', 'manual'),
]

# Manual page output

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'urbs', u'urbs Documentation',
     [u'tum-ens'], 1)
]


# Texinfo output

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'urbs', u'urbs Documentation',
   u'tum-ens', 'urbs', 'A linear optimisation model for distributed energy systems',
   'Miscellaneous'),
]


# Epub output

# Bibliographic Dublin Core info.
epub_title = u'urbs'
epub_author = u'tum-ens'
epub_publisher = u'tum-ens'
epub_copyright = u'2014, tum-ens'

epub_exclude_files = ['search.html']


# Intersphinx

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'http://docs.python.org/': None,
    'pandas': ('http://pandas.pydata.org/pandas-docs/stable/', None),
    'matplotlib': ('http://matplotlib.org/', None)}

