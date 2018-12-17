(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else if(typeof exports === 'object')
		exports["bulmaCarousel"] = factory();
	else
		root["bulmaCarousel"] = factory();
})(typeof self !== 'undefined' ? self : this, function() {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
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
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__events__ = __webpack_require__(1);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__defaultOptions__ = __webpack_require__(2);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }




var BULMA_CAROUSEL_EVENTS = {
  'ready': 'carousel:ready',
  'slideBefore': 'carousel:slide:before',
  'slideAfter': 'carousel:slide:after'
};

var onSwipeStart = Symbol('onSwipeStart');
var onSwipeMove = Symbol('onSwipeMove');
var onSwipeEnd = Symbol('onSwipeEnd');

var supportsPassive = false;
try {
  var opts = Object.defineProperty({}, 'passive', {
    get: function get() {
      supportsPassive = true;
    }
  });
  window.addEventListener("testPassive", null, opts);
  window.removeEventListener("testPassive", null, opts);
} catch (e) {}

var bulmaCarousel = function (_EventEmitter) {
  _inherits(bulmaCarousel, _EventEmitter);

  function bulmaCarousel(selector) {
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

    _classCallCheck(this, bulmaCarousel);

    var _this = _possibleConstructorReturn(this, (bulmaCarousel.__proto__ || Object.getPrototypeOf(bulmaCarousel)).call(this));

    _this.element = typeof selector === 'string' ? document.querySelector(selector) : selector;
    // An invalid selector or non-DOM node has been provided.
    if (!_this.element) {
      throw new Error('An invalid selector or non-DOM node has been provided.');
    }

    _this._clickEvents = ['click'];
    _this.options = Object.assign({}, __WEBPACK_IMPORTED_MODULE_1__defaultOptions__["a" /* default */], options);
    if (_this.element.dataset.autoplay) {
      _this.options.autoplay = _this.element.dataset.autoplay;
    }
    if (_this.element.dataset.delay) {
      _this.options.delay = _this.element.dataset.delay;
    }
    if (_this.element.dataset.size && !_this.element.classList.contains('carousel-animate-fade')) {
      _this.options.size = _this.element.dataset.size;
    }
    if (_this.element.classList.contains('carousel-animate-fade')) {
      _this.options.size = 1;
    }

    _this.forceHiddenNavigation = false;

    _this[onSwipeStart] = _this[onSwipeStart].bind(_this);
    _this[onSwipeMove] = _this[onSwipeMove].bind(_this);
    _this[onSwipeEnd] = _this[onSwipeEnd].bind(_this);

    _this.init();
    return _this;
  }

  /**
   * Initiate all DOM element containing carousel class
   * @method
   * @return {Array} Array of all Carousel instances
   */


  _createClass(bulmaCarousel, [{
    key: 'init',


    /**
     * Initiate plugin
     * @method init
     * @return {void}
     */
    value: function init() {
      this.container = this.element.querySelector('.carousel-container');
      this.items = this.element.querySelectorAll('.carousel-item');
      this.currentItem = {
        element: this.element,
        node: this.element.querySelector('.carousel-item.is-active'),
        pos: -1
      };
      this.currentItem.pos = this.currentItem.node ? Array.from(this.items).indexOf(this.currentItem.node) : -1;
      if (!this.currentItem.node) {
        this.currentItem.node = this.items[0];
        this.currentItem.node.classList.add('is-active');
        this.currentItem.pos = 0;
      }
      this.forceHiddenNavigation = this.items.length <= 1;

      var images = this.element.querySelectorAll('img');
      [].forEach.call(images, function (img) {
        img.setAttribute('draggable', false);
      });

      this._resize();
      this._setOrder();
      this._initNavigation();
      this._bindEvents();

      if (this.options.autoplay) {
        this._autoPlay(this.options.delay);
      }

      this.emit(BULMA_CAROUSEL_EVENTS.ready, this.currentItem);
    }
  }, {
    key: '_resize',
    value: function _resize() {
      var _this2 = this;

      var computedStyle = window.getComputedStyle(this.element);
      var width = parseInt(computedStyle.getPropertyValue('width'), 10);

      // Detect which animation is setup and auto-calculate size and transformation
      if (this.options.size > 1) {
        if (this.options.size >= Array.from(this.items).length) {
          this.offset = 0;
        } else {
          this.offset = width / this.options.size;
        }

        this.container.style.left = 0 - this.offset + 'px';
        this.container.style.transform = 'translateX(' + this.offset + 'px)';
        [].forEach.call(this.items, function (item) {
          item.style.flexBasis = _this2.offset + 'px';
        });
      }

      // If animation is fade then force carouselContainer size (due to the position: absolute)
      if (this.element.classList.contains('carousel-animate-fade') && this.items.length) {
        var img = this.items[0].querySelector('img');
        var scale = 1;
        if (img.naturalWidth) {
          scale = width / img.naturalWidth;
          this.container.style.height = img.naturalHeight * scale + 'px';
        } else {
          img.onload = function () {
            scale = width / img.naturalWidth;
            _this2.container.style.height = img.naturalHeight * scale + 'px';
          };
        }
      }
    }

    /**
     * Bind all events
     * @method _bindEvents
     * @return {void}
     */

  }, {
    key: '_bindEvents',
    value: function _bindEvents() {
      var _this3 = this;

      if (this.previousControl) {
        this._clickEvents.forEach(function (clickEvent) {
          _this3.previousControl.addEventListener(clickEvent, function (e) {
            if (!supportsPassive) {
              e.preventDefault();
            }
            if (_this3._autoPlayInterval) {
              clearInterval(_this3._autoPlayInterval);
              _this3._autoPlay(_this3.optionsdelay);
            }
            _this3._slide('previous');
          }, supportsPassive ? { passive: true } : false);
        });
      }

      if (this.nextControl) {
        this._clickEvents.forEach(function (clickEvent) {
          _this3.nextControl.addEventListener(clickEvent, function (e) {
            if (!supportsPassive) {
              e.preventDefault();
            }
            if (_this3._autoPlayInterval) {
              clearInterval(_this3._autoPlayInterval);
              _this3._autoPlay(_this3.options.delay);
            }
            _this3._slide('next');
          }, supportsPassive ? { passive: true } : false);
        });
      }

      // Bind swipe events
      this.element.addEventListener('touchstart', this[onSwipeStart], supportsPassive ? { passive: true } : false);
      this.element.addEventListener('mousedown', this[onSwipeStart], supportsPassive ? { passive: true } : false);
      this.element.addEventListener('touchmove', this[onSwipeMove], supportsPassive ? { passive: true } : false);
      this.element.addEventListener('mousemove', this[onSwipeMove], supportsPassive ? { passive: true } : false);
      this.element.addEventListener('touchend', this[onSwipeEnd], supportsPassive ? { passive: true } : false);
      this.element.addEventListener('mouseup', this[onSwipeEnd], supportsPassive ? { passive: true } : false);
    }
  }, {
    key: 'destroy',
    value: function destroy() {
      this.element.removeEventListener('touchstart', this[onSwipeStart], supportsPassive ? { passive: true } : false);
      this.element.removeEventListener('mousedown', this[onSwipeStart], supportsPassive ? { passive: true } : false);
      this.element.removeEventListener('touchmove', this[onSwipeMove], supportsPassive ? { passive: true } : false);
      this.element.removeEventListener('mousemove', this[onSwipeMove], supportsPassive ? { passive: true } : false);
      this.element.removeEventListener('touchend', this[onSwipeEnd], supportsPassive ? { passive: true } : false);
      this.element.removeEventListener('mouseup', this[onSwipeEnd], supportsPassive ? { passive: true } : false);
    }

    /**
     * Save current position on start swiping
     * @method onSwipeStart
     * @param  {Event}    e Swipe event
     * @return {void}
     */

  }, {
    key: onSwipeStart,
    value: function value(e) {
      if (!supportsPassive) {
        e.preventDefault();
      }

      e = e ? e : window.event;
      e = 'changedTouches' in e ? e.changedTouches[0] : e;
      this._touch = {
        start: {
          time: new Date().getTime(), // record time when finger first makes contact with surface
          x: e.pageX,
          y: e.pageY
        },
        dist: {
          x: 0,
          y: 0
        }
      };
    }

    /**
     * Save current position on end swiping
     * @method onSwipeMove
     * @param  {Event}  e swipe event
     * @return {void}
     */

  }, {
    key: onSwipeMove,
    value: function value(e) {
      if (!supportsPassive) {
        e.preventDefault();
      }
    }

    /**
     * Save current position on end swiping
     * @method onSwipeEnd
     * @param  {Event}  e swipe event
     * @return {void}
     */

  }, {
    key: onSwipeEnd,
    value: function value(e) {
      if (!supportsPassive) {
        e.preventDefault();
      }

      e = e ? e : window.event;
      e = 'changedTouches' in e ? e.changedTouches[0] : e;
      this._touch.dist = {
        x: e.pageX - this._touch.start.x, // get horizontal dist traveled by finger while in contact with surface
        y: e.pageY - this._touch.start.y // get vertical dist traveled by finger while in contact with surface
      };

      this._handleGesture();
    }

    /**
     * Identify the gestureand slide if necessary
     * @method _handleGesture
     * @return {void}
     */

  }, {
    key: '_handleGesture',
    value: function _handleGesture() {
      var elapsedTime = new Date().getTime() - this._touch.start.time; // get time elapsed
      if (elapsedTime <= this.options.allowedTime) {
        // first condition for awipe met
        if (Math.abs(this._touch.dist.x) >= this.options.threshold && Math.abs(this._touch.dist.y) <= this.options.restraint) {
          // 2nd condition for horizontal swipe met
          this._touch.dist.x < 0 ? this._slide('next') : this._slide('previous'); // if dist traveled is negative, it indicates left swipe
        }
      }
    }

    /**
     * Initiate Navigation area and Previous/Next buttons
     * @method _initNavigation
     * @return {[type]}        [description]
     */

  }, {
    key: '_initNavigation',
    value: function _initNavigation() {
      this.previousControl = this.element.querySelector('.carousel-nav-left');
      this.nextControl = this.element.querySelector('.carousel-nav-right');

      if (this.items.length <= 1 || this.forceHiddenNavigation) {
        if (this.container) {
          this.container.style.left = '0';
        }
        if (this.previousControl) {
          this.previousControl.style.display = 'none';
        }
        if (this.nextControl) {
          this.nextControl.style.display = 'none';
        }
      }
    }

    /**
     * Update each item order
     * @method _setOrder
     */

  }, {
    key: '_setOrder',
    value: function _setOrder() {
      this.currentItem.node.style.order = '1';
      this.currentItem.node.style.zIndex = '1';
      var item = this.currentItem.node;
      var i = void 0,
          j = void 0,
          ref = void 0;
      for (i = j = 2, ref = Array.from(this.items).length; 2 <= ref ? j <= ref : j >= ref; i = 2 <= ref ? ++j : --j) {
        item = this._next(item);
        item.style.order = '' + i % Array.from(this.items).length;
        item.style.zIndex = '0';
      }
    }

    /**
     * Find next item to display
     * @method _next
     * @param  {Node} element Current Node element
     * @return {Node}         Next Node element
     */

  }, {
    key: '_next',
    value: function _next(element) {
      if (element.nextElementSibling) {
        return element.nextElementSibling;
      } else {
        return this.items[0];
      }
    }

    /**
     * Find previous item to display
     * @method _previous
     * @param  {Node}  element Current Node element
     * @return {Node}          Previous Node element
     */

  }, {
    key: '_previous',
    value: function _previous(element) {
      if (element.previousElementSibling) {
        return element.previousElementSibling;
      } else {
        return this.items[this.items.length - 1];
      }
    }

    /**
     * Update slides to display the wanted one
     * @method _slide
     * @param  {String} [direction='next'] Direction in which items need to move
     * @return {void}
     */

  }, {
    key: '_slide',
    value: function _slide() {
      var _this4 = this;

      var direction = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 'next';

      if (this.items.length) {
        this.oldItemNode = this.currentItem.node;
        this.emit(BULMA_CAROUSEL_EVENTS.slideBefore, this.currentItem);
        // initialize direction to change order
        if (direction === 'previous') {
          this.currentItem.node = this._previous(this.currentItem.node);
          // add reverse class
          if (!this.element.classList.contains('carousel-animate-fade')) {
            this.element.classList.add('is-reversing');
            this.container.style.transform = 'translateX(' + -Math.abs(this.offset) + 'px)';
          }
        } else {
          // Reorder items
          this.currentItem.node = this._next(this.currentItem.node);
          // re_slide reverse class
          this.element.classList.remove('is-reversing');
          this.container.style.transform = 'translateX(' + Math.abs(this.offset) + 'px)';
        }
        this.currentItem.node.classList.add('is-active');
        this.oldItemNode.classList.remove('is-active');

        // Disable transition to instant change order
        this.element.classList.remove('carousel-animated');
        // Enable transition to animate order 1 to order 2
        setTimeout(function () {
          _this4.element.classList.add('carousel-animated');
        }, 50);

        this._setOrder();
        this.emit(BULMA_CAROUSEL_EVENTS.slideAfter, this.currentItem);
      }
    }

    /**
     * Initiate autoplay system
     * @method _autoPlay
     * @param  {Number}  [delay=5000] Delay between slides in milliseconds
     * @return {void}
     */

  }, {
    key: '_autoPlay',
    value: function _autoPlay() {
      var _this5 = this;

      var delay = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 5000;

      this._autoPlayInterval = setInterval(function () {
        _this5._slide('next');
      }, delay);
    }
  }], [{
    key: 'attach',
    value: function attach() {
      var selector = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : '.carousel, .hero-carousel';
      var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

      var instances = new Array();

      var elements = document.querySelectorAll(selector);
      [].forEach.call(elements, function (element) {
        setTimeout(function () {
          instances.push(new bulmaCarousel(element, options));
        }, 100);
      });
      return instances;
    }
  }]);

  return bulmaCarousel;
}(__WEBPACK_IMPORTED_MODULE_0__events__["a" /* default */]);

/* harmony default export */ __webpack_exports__["default"] = (bulmaCarousel);

/***/ }),
/* 1 */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var EventEmitter = function () {
  function EventEmitter() {
    var listeners = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];

    _classCallCheck(this, EventEmitter);

    this._listeners = new Map(listeners);
    this._middlewares = new Map();
  }

  _createClass(EventEmitter, [{
    key: "listenerCount",
    value: function listenerCount(eventName) {
      if (!this._listeners.has(eventName)) {
        return 0;
      }

      var eventListeners = this._listeners.get(eventName);
      return eventListeners.length;
    }
  }, {
    key: "removeListeners",
    value: function removeListeners() {
      var _this = this;

      var eventName = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
      var middleware = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;

      if (eventName !== null) {
        if (Array.isArray(eventName)) {
          name.forEach(function (e) {
            return _this.removeListeners(e, middleware);
          });
        } else {
          this._listeners.delete(eventName);

          if (middleware) {
            this.removeMiddleware(eventName);
          }
        }
      } else {
        this._listeners = new Map();
      }
    }
  }, {
    key: "middleware",
    value: function middleware(eventName, fn) {
      var _this2 = this;

      if (Array.isArray(eventName)) {
        name.forEach(function (e) {
          return _this2.middleware(e, fn);
        });
      } else {
        if (!Array.isArray(this._middlewares.get(eventName))) {
          this._middlewares.set(eventName, []);
        }

        this._middlewares.get(eventName).push(fn);
      }
    }
  }, {
    key: "removeMiddleware",
    value: function removeMiddleware() {
      var _this3 = this;

      var eventName = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;

      if (eventName !== null) {
        if (Array.isArray(eventName)) {
          name.forEach(function (e) {
            return _this3.removeMiddleware(e);
          });
        } else {
          this._middlewares.delete(eventName);
        }
      } else {
        this._middlewares = new Map();
      }
    }
  }, {
    key: "on",
    value: function on(name, callback) {
      var _this4 = this;

      var once = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;

      if (Array.isArray(name)) {
        name.forEach(function (e) {
          return _this4.on(e, callback);
        });
      } else {
        name = name.toString();
        var split = name.split(/,|, | /);

        if (split.length > 1) {
          split.forEach(function (e) {
            return _this4.on(e, callback);
          });
        } else {
          if (!Array.isArray(this._listeners.get(name))) {
            this._listeners.set(name, []);
          }

          this._listeners.get(name).push({ once: once, callback: callback });
        }
      }
    }
  }, {
    key: "once",
    value: function once(name, callback) {
      this.on(name, callback, true);
    }
  }, {
    key: "emit",
    value: function emit(name, data) {
      var _this5 = this;

      var silent = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;

      name = name.toString();
      var listeners = this._listeners.get(name);
      var middlewares = null;
      var doneCount = 0;
      var execute = silent;

      if (Array.isArray(listeners)) {
        listeners.forEach(function (listener, index) {
          // Start Middleware checks unless we're doing a silent emit
          if (!silent) {
            middlewares = _this5._middlewares.get(name);
            // Check and execute Middleware
            if (Array.isArray(middlewares)) {
              middlewares.forEach(function (middleware) {
                middleware(data, function () {
                  var newData = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;

                  if (newData !== null) {
                    data = newData;
                  }
                  doneCount++;
                }, name);
              });

              if (doneCount >= middlewares.length) {
                execute = true;
              }
            } else {
              execute = true;
            }
          }

          // If Middleware checks have been passed, execute
          if (execute) {
            if (listener.once) {
              listeners[index] = null;
            }
            listener.callback(data);
          }
        });

        // Dirty way of removing used Events
        while (listeners.indexOf(null) !== -1) {
          listeners.splice(listeners.indexOf(null), 1);
        }
      }
    }
  }]);

  return EventEmitter;
}();

/* harmony default export */ __webpack_exports__["a"] = (EventEmitter);

/***/ }),
/* 2 */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
var defaultOptions = {
  size: 1,
  autoplay: false,
  delay: 5000,
  threshold: 50, //required min distance traveled to be considered swipe
  restraint: 100, // maximum distance allowed at the same time in perpendicular direction
  allowedTime: 500 // maximum time allowed to travel that distance
};

/* harmony default export */ __webpack_exports__["a"] = (defaultOptions);

/***/ })
/******/ ])["default"];
});