// Define variables.
var autoprefixer    = require('autoprefixer');
var cleancss        = require('gulp-clean-css');
var concat          = require('gulp-concat');
var del             = require('del');
var gulp            = require('gulp');
var gutil           = require('gulp-util');
var imagemin        = require('gulp-imagemin');
var imageminMozjpeg = require('imagemin-mozjpeg');
var notify          = require('gulp-notify');
var postcss         = require('gulp-postcss');
var rename          = require('gulp-rename');
var run             = require('gulp-run');
var runSequence     = require('run-sequence');
var sass            = require('gulp-ruby-sass');
var uglify          = require('gulp-uglify');
var htmlmin         = require('gulp-htmlmin');
var inliner         = require('gulp-inline-source');
var fontMagician    = require('postcss-font-magician');

var paths           = require('./paths');

gulp.task('build:styles:main', function() {
    return gulp.src(paths.cssFiles + '/style.css')
        .pipe(postcss([ autoprefixer({ browsers: ['last 2 versions'] }) ]))
        .pipe(cleancss())
        .pipe(gulp.dest(paths.siteCssFiles))
        .on('error', gutil.log);
});

// Processes critical CSS, to be included in head.html.
gulp.task('build:styles:critical', function() {
    return gulp.src(paths.cssFiles + '/critical.css')
        .pipe(postcss([
          autoprefixer({ browsers: ['last 2 versions'] }),
          fontMagician({
            variants: {
              'Source Sans Pro': { '300': ['woff, woff2'], '400': ['woff, woff2'], '400i': ['woff, woff2'], '700': ['woff, woff2'] },
              'Anonymous Pro': { '400': ['woff, woff2'], '700': ['woff, woff2'] }
            }
          })
        ])).pipe(cleancss())
        .pipe(concat('compiled_critical.css'))
        .pipe(gulp.dest(paths.cssFiles))
        .on('error', gutil.log);
});

// Builds all styles.
gulp.task('build:styles', ['build:styles:main', 'build:styles:critical']);

gulp.task('clean:styles', function(callback) {
    del([paths.siteCssFiles + '/style.css',
        paths.cssFiles + '/compiled_critical.css'
    ]);
    callback();
});

// Concatenates and uglifies global JS files and outputs result to the
// appropriate location.
gulp.task('build:scripts:global', function() {
    return gulp.src([
        paths.jsFiles + '/lib' + paths.jsPattern,
        paths.jsFiles + '/*.js'
    ])
        .pipe(concat('script.js'))
        .pipe(uglify()).on('error', function (err) { gutil.log(gutil.colors.red('[Error]'), err.toString()); })
        .pipe(gulp.dest(paths.siteJsFiles))
        .on('error', gutil.log);
});

gulp.task('clean:scripts', function(callback) {
    del([paths.siteJsFiles + '/script.js']);
    callback();
});

// Concatenates and uglifies leaflet JS files and outputs result to the
// appropriate location.
gulp.task('build:scripts:leaflet', function() {
    return gulp.src([
        paths.jsFiles + '/leaflet/leaflet.js',
        paths.jsFiles + '/leaflet/leaflet-providers.js'
    ])
        .pipe(concat('leaflet.js'))
        .pipe(uglify())
        .pipe(gulp.dest(paths.siteJsFiles))
        .on('error', gutil.log);
});

gulp.task('clean:scripts:leaflet', function(callback) {
    del([paths.siteJsFiles + '/leaflet.js']);
    callback();
});

// Builds all scripts.
gulp.task('build:scripts', ['build:scripts:global', 'build:scripts:leaflet']);

// Optimizes and copies image files.
gulp.task('build:images', function() {
    return gulp.src(paths.imageFilesGlob)
        .pipe(imagemin([ imageminMozjpeg({ quality: 70 }) ]))
        .pipe(gulp.dest(paths.siteImageFiles));
});

gulp.task('clean:images', function(callback) {
    del([paths.siteImageFiles]);
    callback();
});

gulp.task('build:assets', function() {
    return gulp.src(paths.assetFilesGlob)
        .pipe(gulp.dest(paths.siteAssetFiles));
});

gulp.task('clean:assets', function(callback) {
    del([paths.siteAssetFiles]);
    callback();
});

// Copies fonts.
gulp.task('build:fonts', ['fontawesome']);

// Places Font Awesome fonts in proper location.
gulp.task('fontawesome', function() {
    return gulp.src(paths.fontFiles + '/font-awesome/**.*')
        .pipe(rename(function(path) {path.dirname = '';}))
        .pipe(gulp.dest(paths.siteFontFiles))
        .on('error', gutil.log);
});

gulp.task('clean:fonts', function(callback) {
    del([paths.siteFontFiles]);
    callback();
});

gulp.task('html', function() {
    gulp.src(paths.srcHtmlFolderName + '/**/*.html')
        .pipe(inliner({ rootpath : paths.srcHtmlFolderName }))
        .pipe(htmlmin({collapseWhitespace: true}))
        .pipe(gulp.dest(paths.siteDir));
});

gulp.task('build:docs:html', function() {
    return gulp.src('')
        .pipe(run('python make_docs.py'))
        .on('error', gutil.log);
});

// Deletes the entire _site directory.
gulp.task('clean:docs', function(callback) {
    del([paths.srcHtmlFolderName, paths.siteDir]);
    callback();
});

gulp.task('clean', ['clean:docs',
    'clean:fonts',
    'clean:images',
    'clean:assets',
    'clean:scripts',
    'clean:styles']);

// Builds site anew.
gulp.task('build', function(callback) {
    runSequence('clean', 'build:docs:html',
        ['build:scripts', 'build:images', 'build:assets', 'build:styles', 'build:fonts'],
        'html', callback);
});

// Default Task: builds site.
gulp.task('default', ['build']);

// Updates Ruby gems
gulp.task('update:bundle', function() {
    return gulp.src('')
        .pipe(run('bundle install'))
        .pipe(run('bundle update'))
        .pipe(notify({ message: 'Bundle Update Complete' }))
        .on('error', gutil.log);
}); 
