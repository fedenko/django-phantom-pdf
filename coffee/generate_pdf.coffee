# Create a page object
page = require('webpage').create()
# Require the system module so I can read the command line arguments
system = require('system')
# Require the FileSystem module, so I can read the cookie file

console.error = ->
  system.stderr.write Array::join.call(arguments, ' ') + '\n'
  return

fs = require('fs')
# Read the url and output file location from the command line argument
# Read the cookie file and split it by spaces
# Because the way I constructed this file, separate each field using spaces
sformat = (template, data) ->
  template.replace /{{(.*?)}}/g, (m, n) ->
    eval 'data.' + n

address = system.args[1]
output = system.args[2]
cookies = JSON.parse(system.args[3])
acceptLanguage = system.args[4]
paperSize = JSON.parse(system.args[5])
viewportSize = JSON.parse(system.args[6]) if system.args.length >= 7
compensateForPhantomV2PdfRenderingBug = parseFloat(system.args[7]) if system.args.length == 8


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
    header_contents = paperSize.header.contents
    paperSize.header.contents = phantom.callback((pageNum, numPages) ->
      sformat header_contents,
        page_num: pageNum
        num_pages: numPages
    )
    # console.log paperSize.header.contents
if paperSize.footer
  if paperSize.footer.contents
    footer_contents = paperSize.footer.contents
    paperSize.footer.contents = phantom.callback((pageNum, numPages) ->
      sformat footer_contents,
        page_num: pageNum
        num_pages: numPages
    )
    # console.log paperSize.footer.contents

page.paperSize = paperSize
page.viewportSize = viewportSize if Object.keys(viewportSize).length


# Now we have everything settled, let's render the page

page.open address, (status) ->
  if status != 'success'
    # If PhantomJS failed to reach the address, print a message
    console.error "Unable to load the address \"#{address}\""
    phantom.exit(1)
  else
    # Now create the output file and exit PhantomJS
    if compensateForPhantomV2PdfRenderingBug > 0 and compensateForPhantomV2PdfRenderingBug != 1
      page.evaluate ((zoom) ->
        document.querySelector('body').style.zoom = zoom
        ), compensateForPhantomV2PdfRenderingBug
    page.render output
    phantom.exit(0)
  return
