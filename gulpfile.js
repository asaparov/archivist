// Define variables.
import autoprefixer			from 'autoprefixer';
import cleancss				from 'gulp-clean-css';
import concat				from 'gulp-concat';
import del					from 'del';
import gulp					from 'gulp';
const {src, dest, series, parallel} = gulp;
import log					from 'fancy-log';
import imagemin, {mozjpeg}	from 'gulp-imagemin';
import notify				from 'gulp-notify';
import postcss				from 'gulp-postcss';
import rename				from 'gulp-rename';
import run					from 'gulp-run';
import uglify				from 'gulp-uglify';
import htmlmin				from 'gulp-htmlmin';
import inliner				from 'gulp-inline-source';
import fontMagician			from 'postcss-font-magician';
import cp					from 'child_process';

import {paths}				from './paths.js';

function build_styles_main() {
	return src(paths.cssFiles + '/style.css')
		.pipe(postcss([ autoprefixer({ overrideBrowserslist: ['last 2 versions'] }) ]))
		.pipe(cleancss())
		.pipe(dest(paths.siteCssFiles))
		.on('error', log.error);
}

// Processes critical CSS, to be included in head.html.
function build_styles_critical() {
	return src(paths.cssFiles + '/critical.css')
		.pipe(postcss([
			autoprefixer({ overrideBrowserslist: ['last 2 versions'] }),
			fontMagician({
				variants: {
					'Source Sans Pro': { '300': ['woff, woff2'], '400': ['woff, woff2'], '400i': ['woff, woff2'], '700': ['woff, woff2'] },
					'Anonymous Pro': { '400': ['woff, woff2'], '700': ['woff, woff2'] }
				}
			})
		])).pipe(cleancss())
		.pipe(concat('compiled_critical.css'))
		.pipe(dest(paths.cssFiles))
		.on('error', log.error);
}

// Builds all styles.
const build_styles = parallel(build_styles_main, build_styles_critical);

function clean_styles(callback) {
	return del([paths.siteCssFiles + '/style.css',
		paths.cssFiles + '/compiled_critical.css'
	]).then(function(result) {callback();});
}

// Concatenates and uglifies global JS files and outputs result to the
// appropriate location.
function build_scripts_global() {
	return src([
		paths.jsFiles + '/lib' + paths.jsPattern,
		paths.jsFiles + '/*.js'
	])
		.pipe(concat('script.js'))
		.pipe(uglify()).on('error', function (err) { log.error(err.toString()); })
		.pipe(dest(paths.siteJsFiles))
		.on('error', log.error);
}

function clean_scripts(callback) {
	return del([paths.siteJsFiles + '/script.js'])
		.then(function(result) {callback();});
}

// Builds all scripts.
const build_scripts = parallel(build_scripts_global);

// Optimizes and copies image files.
function build_images() {
	return src(paths.imageFilesGlob)
		.pipe(imagemin([ mozjpeg({ quality: 70 }) ]))
		.pipe(dest(paths.siteImageFiles));
}

function clean_images(callback) {
	return del([paths.siteImageFiles])
		.then(function(result) {callback();});
}

function build_assets() {
	return src(paths.assetFilesGlob)
		.pipe(dest(paths.siteAssetFiles));
}

function clean_assets(callback) {
	return del([paths.siteAssetFiles])
		.then(function(result) {callback();});
}

// Places Font Awesome fonts in proper location.
function fontawesome() {
	return src(paths.fontFiles + '/font-awesome/**.*')
		.pipe(rename(function(path) {path.dirname = '';}))
		.pipe(dest(paths.siteFontFiles))
		.on('error', log.error);
}

// Copies fonts.
const build_fonts = series(fontawesome);

function clean_fonts(callback) {
	return del([paths.siteFontFiles])
		.then(function(result) {callback();});
}

function html() {
	return src(paths.srcHtmlFolderName + '/**/*.html')
		.pipe(inliner({ rootpath : paths.srcHtmlFolderName }))
		.pipe(htmlmin({collapseWhitespace: true}))
		.pipe(dest(paths.siteDir));
}

function build_docs_xml(callback) {
	cp.execSync('doxygen Doxyfile', {stdio:[0,1,2]});
	callback();
}

function build_docs_html() {
	return run('python make_docs.py').exec()
		.on('error', log.error);
}

// Deletes the entire _site directory.
function clean_docs(callback) {
	return del([paths.srcXmlFolderName, paths.srcHtmlFolderName, paths.siteDir])
		.then(function(result) {callback();});
}

const clean = parallel(
	clean_docs,
	clean_fonts,
	clean_images,
	clean_assets,
	clean_scripts,
	clean_styles);

// Builds site anew.
const build = series(clean, build_docs_xml, build_docs_html,
		parallel(build_scripts, build_images, build_assets, build_styles, build_fonts),
		html);

// Default Task: builds site.
export default build;

// Updates Ruby gems
function update_bundle() {
	return src('')
		.pipe(run('bundle install'))
		.pipe(run('bundle update'))
		.pipe(notify({ message: 'Bundle Update Complete' }))
		.on('error', log.error);
}
