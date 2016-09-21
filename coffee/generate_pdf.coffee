# Create a page object
page = require('webpage').create()
# Require the system module so I can read the command line arguments
system = require('system')
# Require the FileSystem module, so I can read the cookie file
fs = require('fs')
# Read the url and output file location from the command line argument
# Read the cookie file and split it by spaces
# Because the way I constructed this file, separate each field using spaces
nunjucks = require('nunjucks')
nunjucks.configure autoescape: true

address = system.args[1]
output = system.args[2]
cookies = JSON.parse(system.args[3])
acceptLanguage = system.args[4]
paperSize = JSON.parse(system.args[5])


# Now we can add cookies into phantomjs, so when it renders the page, it
# will have the same permission and data as the current user

for domain, domain_cookies of cookies
  for name, value of domain_cookies
    phantom.addCookie
      'domain': domain
      'name': name
      'value': value

page.customHeaders = 'Accept-Language': acceptLanguage

# Set the page size and orientation
if paperSize.header
  if paperSize.header.contents
    header_contents = paperSize.footer.contents
    paperSize.header.contents = phantom.callback((pageNum, numPages) ->
      nunjucks.renderString header_contents,
        page_num: pageNum
        num_pages: pageNum
    )
    # console.log paperSize.header.contents
if paperSize.footer
  if paperSize.footer.contents
    footer_contents = paperSize.footer.contents
    paperSize.footer.contents = phantom.callback((pageNum, numPages) ->
      nunjucks.renderString footer_contents,
        page_num: pageNum
        num_pages: pageNum
    )
    # console.log paperSize.footer.contents

page.paperSize = paperSize


# console.log address
# console.log output
# console.log cookies
# console.log acceptLanguage
# console.log format
# console.log orientation
# console.log margin
# console.log paperSize,
# Now we have everything settled, let's render the page

page.open address, (status) ->
  if status != 'success'
    # If PhantomJS failed to reach the address, print a message
    console.log 'Unable to load the address!'
    phantom.exit()
  else
    # Now create the output file and exit PhantomJS
    # cookies = page.cookies
    # console.log 'Listing cookies:'
    # for i of cookies
    #   console.log cookies[i].name + '=' + cookies[i].value
    page.render output
    phantom.exit()
  return
