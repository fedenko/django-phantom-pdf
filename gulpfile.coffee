gulp             = require 'gulp'
plumber          = require 'gulp-plumber'
sourcemaps       = require 'gulp-sourcemaps'
webpack          = require 'webpack-stream'

#
# webpack (CoffeeScript, require)
#
gulp.task 'scripts', ->
  gulp.src './coffee/generate_pdf.coffee'
    .pipe plumber()
    .pipe webpack
      entry:
        generate_pdf: './coffee/generate_pdf.coffee'
      output:
        filename: '[name].js'
        publicPath: '/phantom_pdf_bin/'
      resolve:
        extensions: ['', '.js', '.coffee']
        modulesDirectories: [ 'coffee', 'node_modules'],
      module:
        loaders: [
          { test: /\.coffee$/, loader: 'coffee-loader' }
        ]
      devtool: 'source-map'
      externals:
        webpage: "commonjs webpage"
        system: "commonjs system"
        fs: "commonjs fs"
    .pipe gulp.dest './phantom_pdf_bin'

#
# build assets
#
gulp.task 'build', ['scripts']

#
# Watch
#
gulp.task 'watch', ->
  gulp.watch 'coffee/**/*.+(js|coffee)', ['scripts']


#
# default
#
gulp.task 'default', ['build']
