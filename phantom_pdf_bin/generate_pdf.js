/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;
/******/
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/phantom_pdf_bin/";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	var acceptLanguage, address, compensateForPhantomV2PdfRenderingBug, cookies, domain, domain_cookies, footer_contents, fs, header_contents, name, output, page, paperSize, sformat, system, value, viewportSize;
	
	page = __webpack_require__(1).create();
	
	system = __webpack_require__(2);
	
	console.error = function() {
	  system.stderr.write(Array.prototype.join.call(arguments, ' ') + '\n');
	};
	
	fs = __webpack_require__(3);
	
	sformat = function(template, data) {
	  return template.replace(/{{(.*?)}}/g, function(m, n) {
	    return eval('data.' + n);
	  });
	};
	
	address = system.args[1];
	
	output = system.args[2];
	
	cookies = JSON.parse(system.args[3]);
	
	acceptLanguage = system.args[4];
	
	paperSize = JSON.parse(system.args[5]);
	
	if (system.args.length >= 7) {
	  viewportSize = JSON.parse(system.args[6]);
	}
	
	if (system.args.length === 8) {
	  compensateForPhantomV2PdfRenderingBug = parseFloat(system.args[7]);
	}
	
	for (domain in cookies) {
	  domain_cookies = cookies[domain];
	  for (name in domain_cookies) {
	    value = domain_cookies[name];
	    phantom.addCookie({
	      'domain': domain,
	      'name': name,
	      'value': value
	    });
	  }
	}
	
	page.customHeaders = {
	  'Accept-Language': acceptLanguage
	};
	
	if (paperSize.header) {
	  if (paperSize.header.contents) {
	    header_contents = paperSize.header.contents;
	    paperSize.header.contents = phantom.callback(function(pageNum, numPages) {
	      return sformat(header_contents, {
	        page_num: pageNum,
	        num_pages: numPages
	      });
	    });
	  }
	}
	
	if (paperSize.footer) {
	  if (paperSize.footer.contents) {
	    footer_contents = paperSize.footer.contents;
	    paperSize.footer.contents = phantom.callback(function(pageNum, numPages) {
	      return sformat(footer_contents, {
	        page_num: pageNum,
	        num_pages: numPages
	      });
	    });
	  }
	}
	
	page.paperSize = paperSize;
	
	if (Object.keys(viewportSize).length) {
	  page.viewportSize = viewportSize;
	}
	
	page.open(address, function(status) {
	  if (status !== 'success') {
	    console.error("Unable to load the address \"" + address + "\"");
	    phantom.exit(1);
	  } else {
	    if (compensateForPhantomV2PdfRenderingBug > 0 && compensateForPhantomV2PdfRenderingBug !== 1) {
	      page.evaluate((function(zoom) {
	        return document.querySelector('body').style.zoom = zoom;
	      }), compensateForPhantomV2PdfRenderingBug);
	    }
	    page.render(output);
	    phantom.exit(0);
	  }
	});


/***/ },
/* 1 */
/***/ function(module, exports) {

	module.exports = require("webpage");

/***/ },
/* 2 */
/***/ function(module, exports) {

	module.exports = require("system");

/***/ },
/* 3 */
/***/ function(module, exports) {

	module.exports = require("fs");

/***/ }
/******/ ]);
//# sourceMappingURL=generate_pdf.js.map