"use strict";

// RPC wrapper
function invoke_rpc(method, args, timeout, on_done) {
  hide($("#crash"));
  hide($("#timeout"));
  show($("#rpc_spinner"));
  //send RPC with whatever data is appropriate. Display an error message on crash or timeout
  var xhr = new XMLHttpRequest();
  xhr.open("POST", method, true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.timeout = timeout;
  xhr.send(JSON.stringify(args));
  xhr.ontimeout = function () {
    show($("#timeout"));
    hide($("#rpc_spinner"));
    hide($("#crash"));
  };
  xhr.onloadend = function () {
    if (xhr.status === 200) {
      hide($("#rpc_spinner"));
      var board = JSON.parse(xhr.responseText)
      hide($("#timeout"));
      if (typeof (on_done) != "undefined") {
        on_done(board);
      }
    } else {
      show($("#crash"));
    }
  }
}

// Resource load wrapper
function load_resource(name, on_done) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", name, true);
  xhr.onloadend = function () {
    if (xhr.status === 200) {
      var board = JSON.parse(xhr.responseText);
      on_done(board);
    }
  }
  xhr.send();
}

// Code that runs first
$(document).ready(function () {
  invoke_rpc("/restart", {}, 0, function () { init(); })
});

function restart() {
  invoke_rpc("/restart", {})
}

//  LAB CODE

// this is inlined into infra/ui/ui.js

const SVGNS = 'http://www.w3.org/2000/svg';
var chosen_dim_x = 0;
var chosen_dim_y = 0;
var chosen_slice;
var dimensions;
var xray_state;
var current_focused_square;

var render_board;

var SQUARE_SIZE = 30;
var DEFAULT_DIMENSIONS = "[10, 10]";

// --------------------- init functions ------------------------//

function init_board() {
  var error = false;
  var new_dimensions = get_size(function(err, msg) {
    signal_input_error(msg);
    error = true;
  });

  if (error) {
    return;
  }

  change_xray_state("VISIBLE OFF (v)");
  xray_state = false;

  change_board_state("NEW GAME!");

  // to prevent error from overwriting the previous valid game
  dimensions = new_dimensions;

  chosen_dim_y = 0;
  if (dimensions.length > 1) {
    chosen_dim_x = 1;
  } else {
    chosen_dim_x = 0;
  }

  setup_selectors();

  chosen_slice = dimensions.map(function() {
    return 0;
  });

  var board_rows = dimensions[chosen_dim_y];
  var board_cols = dimensions[chosen_dim_x];

  var width = board_cols * SQUARE_SIZE;
  var height = board_rows * SQUARE_SIZE;

  var num_bombs = get_num_bombs();
  var bomb_list = new_random_game(num_bombs);

  invoke_rpc("/ui_new_game_nd", get_args({bombs: bomb_list}), 0, function () {
    render_rpc(0, 0);
  });
}

function init() {
  init_board();
  init_gui();
}

function get_num_bombs() {
  var num_dims = dimensions.length;
  var av = dimensions.reduce(function(a,b) {return a+b})/num_dims;
  return Math.floor(Math.pow(av, num_dims/2));
}

// -------------------- interaction logic ----------------------//

function hide($object) {
  $object.css({
    display: 'none'
  });
}

function show($object) {
  $object.css({
    display: 'inline-block'
  });
}

var DIRECTIONS = {
  'ArrowUp': 'up',
  'W': 'up',
  'K': 'up',

  'ArrowDown': 'down',
  'S': 'down',
  'J': 'down',

  'ArrowLeft': 'left',
  'A': 'left',
  'H': 'left',

  'ArrowRight': 'right',
  'D': 'right',
  'L': 'right',
}

var DELTAS = {
  "up": [0, -1],
  "down": [0, +1],
  "left": [-1, 0],
  "right": [+1, 0],
}

function init_gui() {
  const svg = document.getElementById('mySvg');

  svg.addEventListener('click', function(evt) {
    var mousePos = get_square(svg, evt);
    if (mousePos.x < 0 || mousePos.y < 0) {
      return
    }

    if (!xray_state) {
      dig_square(mousePos.y, mousePos.x);
    }
  }, false);
  svg.addEventListener('keydown', (event) => {
    const focusedElement = document.activeElement;
    if (focusedElement?.tagName !== 'rect') {
      return;
    }

    const mousePos = {
      'x': parseInt(focusedElement.getAttribute('data-col'), 10),
      'y': parseInt(focusedElement.getAttribute('data-row'), 10)
    }

    // changed focused square
    if (DIRECTIONS.hasOwnProperty(event.key)) {
      const delta = DELTAS[DIRECTIONS[event.key]];
      const [newX, newY] = [mousePos.x + delta[0], mousePos.y + delta[1]];
      const square = document.getElementById(`(${newY}, ${newX})`);
      if (square) {
        square.focus();
        current_focused_square = square;
      }
    }

    // dig a square
    if (event.key !== 'Enter') {
      return;
    }
    if (!xray_state) {
      dig_square(mousePos.y, mousePos.x);
    }

  }, false);

  $("#dimensions").on('keyup', function (e) {
    if (e.keyCode == 13) {
      handle_new_game();
    }
  });

  show($('#rpc_status'));
}

function get_square(svg, evt) {
  var rect = svg.getBoundingClientRect();
  return {
    x: Math.floor((evt.clientX - rect.left) / SQUARE_SIZE),
    y: Math.floor((evt.clientY - rect.top) / SQUARE_SIZE)
  };
}

function change_board_state(text, type) {
  var liveUpdates = $('#liveUpdates');
  var elt = $('#gameStateText');
  elt.removeClass();
  if (type === 'victory') {
    elt.addClass('win');
  } else if (type === 'defeat') {
    elt.addClass('lose');
  }
  elt.text(text);
  // make text different to NVDA speaks it. [] has no auditory affect
  if (liveUpdates.text() == text) {
    text += ' [] ';
  }
  liveUpdates.text(text)
}

function change_xray_state(text) {
  document.getElementById('xray_button').innerHTML = text;
}

function get_size(onerr) {
  var size_string = document.getElementById('dimensions').value;
  size_string = size_string.replace("[", "").replace("]", "");
  var size;
  try {
    size = parse_size("[" + size_string + "]");
  }
  catch(err) {
    onerr(err, "input incorrectly formatted");
    return;
  }

  if (size.length === 0) {
    onerr(null, "empty array is not valid");
    return;
  }

  size = size.map(function(dim) {
    return Math.max(parseInt(dim), 0);
  });

  size.forEach(function(dim) {
    if (dim === 0) {
      onerr(null, "zero is not a valid dimension");
      return;
    }
  });

  document.getElementById('dimensions').value = JSON.stringify(size);

  return size;
}

function handle_new_game() {
  hide($('#input-error'));
  init_board();
}

function disable_radio() {
  $('#choose-coord input[type="number"]').attr('disabled', false);

  var selected_x = $('input[type="radio"][name="selector_x"]:checked').val();
  var selected_y = $('input[type="radio"][name="selector_y"]:checked').val();

  $($('#choose-coord input[type="number"]')[selected_x]).attr('disabled', true);

  $($('#choose-coord input[type="number"]')[selected_y]).attr('disabled', true);
}

function setup_selectors() {
  var selector_dim = $('#selector>#dim-name>.content');
  var selector_x = $('#selector>#choose-x>.content');
  var selector_y = $('#selector>#choose-y>.content');
  var selector_coord = $('#selector>#choose-coord>.content');

  selector_dim.html('');
  selector_x.html('');
  selector_y.html('');
  selector_coord.html('');

  dimensions.forEach(function(dim, i) {
    var dim_name = $('<div>'+i+'</div>');
    selector_dim.append(dim_name);

    var x_sel = $('<div><input class="mdl-radio__button" type="radio" name="selector_x" value="'+i+'"></div>');

    var y_sel = $('<div><input  class="mdl-radio__button" type="radio" name="selector_y" value="'+i+'"></div>');

    x_sel.on('change', function() {
      disable_radio();
      render_selected();
    });

    y_sel.on('change', function() {
      disable_radio();
      render_selected();
    });

    selector_x.append(x_sel);
    selector_y.append(y_sel);

    var coord_sel = $('<div><input class="coord-sel" type="number" min="0" max="'+(dim-1)+'" value="0"></div>');
    coord_sel.on('input', function() {
      var input = $($('#choose-coord input[type="number"]')[i]);
      var val = input.val();
      val = parseInt(val);
      val = val? val: 0;
      val = Math.max(Math.min(val, dim-1), 0);
      input.val(val);
      render_selected();
    });
    selector_coord.append(coord_sel);
  });

  $('input[type="radio"][name="selector_x"][value="'+chosen_dim_x+'"]').prop("checked", true);
  $('input[type="radio"][name="selector_y"][value="'+chosen_dim_y+'"]').prop("checked", true);

  disable_radio();
};

function render_selected() {
  chosen_dim_x = parseInt($('input[type="radio"][name="selector_x"]:checked').val());
  chosen_dim_y = parseInt($('input[type="radio"][name="selector_y"]:checked').val());

  dimensions.forEach(function(dim, i) {
    var val = parseInt($($('#choose-coord input[type="number"]')[i]).val());
    chosen_slice[i] = val;
  });

  render(render_board);
}

function signal_input_error(msg) {
  $('#input-error #message').text(msg);
  show($('#input-error'));
}

// ------------------- Render logic -------------------------------------//

function render(render_board) {
  // calculate unit for lattice cell
  var board_rows = dimensions[chosen_dim_y];
  var board_cols = dimensions[chosen_dim_x];

  // if it's actually a 1D slice they want
  if (chosen_dim_x === chosen_dim_y) {
    board_rows = 1;
  }

  var width = board_cols * SQUARE_SIZE;
  var height = board_rows * SQUARE_SIZE;

  const svg = document.getElementById('mySvg');
  svg.innerHTML = '';
  const defs = document.createElementNS(SVGNS, 'defs');
  svg.setAttribute('width', board_cols * SQUARE_SIZE);
  svg.setAttribute('height', board_rows * SQUARE_SIZE);
  defs.innerHTML = `
    <style>
      .grid-line {
        stroke: gray;
        stroke-width: 2;
      }
    </style>
  `;
  svg.appendChild(defs);

  // draw lines for each column
  var g = document.createElementNS(SVGNS, 'g');
  g.classList.add('grid-line');
  for (var x = 0; x <= board_cols; x += 1) {
    g.appendChild(draw_line(x * SQUARE_SIZE, 0, x * SQUARE_SIZE, height));
  }
  svg.appendChild(g);

  // draw lines for each row
  var g = document.createElementNS(SVGNS, 'g');
  g.classList.add('grid-line');
  for (var y = 0; y <= board_rows; y += 1) {
    g.appendChild(draw_line(0, y * SQUARE_SIZE, width, y * SQUARE_SIZE));
  }
  svg.appendChild(g);

  // color each square
  // get_value

  // using the recursive getter here
  for (var row = 0; row < board_rows; row++) {
    for (var col = 0; col < board_cols; col++) {
      var coord = chosen_slice.slice();
      coord[chosen_dim_y] = row;
      coord[chosen_dim_x] = col;

      var value = get_value(coord, render_board);

      if (value == '_') {
        const square = draw_square(col, row, 'gray');
        svg.appendChild(square);
        square.setAttribute('aria-label', `covered square at (${row}, ${col})`);
        square.setAttribute('tabindex', '0');
        square.setAttribute('data-row', row);
        square.setAttribute('data-col', col);
        square.setAttribute('id', `(${row}, ${col})`);
        continue;
      }

      const square = draw_square(col, row, 'white')
      svg.appendChild(square);
      square.setAttribute('tabindex', '0');
      square.setAttribute('data-row', row);
      square.setAttribute('data-col', col);
      square.setAttribute('id', `(${row}, ${col})`);

      if (value == '.') {
        square.setAttribute('aria-label', `mine at (${row}, ${col}})`);
        svg.appendChild(draw_mine(col, row));
      }
      else if (value == ' ') {
        //empty cell, pass
        square.setAttribute('aria-label', `uncovered square at (${row}, ${col})`);
      }
      else {
        square.setAttribute('aria-label', `uncovered square at (${row}, ${col}) with ${value} mines around it`);
        svg.appendChild(draw_text(col, row, value));
      }
    }
  }

}

// ---------------------------- game helper logic ---------------------------//

function parse_size(size_string) {
  return JSON.parse(size_string);
}

function new_random_game(num_bombs) {
  var bomb_list = [];

  var bomb_set = new Set();

  var board_rows = dimensions[chosen_dim_y];
  var board_cols = dimensions[chosen_dim_x];

  for (var i = 0; i < num_bombs; i++) {

    var bomb = dimensions.map(function(dim) {
      return Math.floor(Math.random() * (dim));
    });
    bomb_set.add(JSON.stringify(bomb));
  }

  for (var value of bomb_set) {
    bomb_list.push(JSON.parse(value));
  }
  return bomb_list
}

function get_value(coord, board){
  var this_coord = coord[0];

  // Base case
  if (coord.length === 1){
    return board[this_coord]
  }

  // Recursive case
  return get_value(coord.slice(1), board[this_coord])
}

// ----------------------- RPC -----------------------------------------//

function get_args(optional) {
  return {
    "xray": xray_state,
    "bombs": optional && optional.bombs,
    "dimensions": dimensions,
    "coordinates": optional && optional.coordinates,
  };
}

function render_rpc(row, col) {
  invoke_rpc("/ui_render_nd", get_args(), 0, function(result) {
    render_board = result;
    render(render_board);
    if (row === undefined || col === undefined) {
      return;
    }
    // put focus on board square
    setTimeout(() => {
      const square = document.getElementById(`(${row}, ${col})`);
      if (square) {
        square.focus();
        current_focused_square = square;
      }
    }, 20);
  });
}

function handle_xray_button() {
  xray_state = !xray_state;
  var board_text = xray_state? "VISIBLE ON (GAME PAUSED) (v)" : "VISIBLE OFF (v)";

  const mousePos = {
    'x': parseInt(current_focused_square?.getAttribute('data-col') ?? 0, 10),
    'y': parseInt(current_focused_square?.getAttribute('data-row') ?? 0, 10)
  }

  change_xray_state(board_text);

  render_rpc(mousePos.y, mousePos.x);
}

function dig_square(row, col) {
  var coord = chosen_slice.slice();
  coord[chosen_dim_y] = row;
  coord[chosen_dim_x] = col;

  invoke_rpc("/ui_dig_nd", get_args({coordinates: coord}), 0, function (result) {
    var state = result[0];
    var dug = result[1];
    var board_text = '';
    if (state == "victory") {
      board_text = "YOU WIN - YOU CLEARED THE BOARD!";
    }
    else if (state == "defeat") {
      board_text = "YOU LOSE - YOU DUG A BOMB!";
    }
    else if (state == "ongoing") {
      board_text = "GOOD MOVE - YOU DUG " + dug + " SQUARES!";
    }
    else {
      board_text = "ERROR - CHECK YOUR GAME STATUS!";
    }
    change_board_state(board_text, state);

    render_rpc(row, col);
  });
}


// ----------------- svg drawing functions -------------------- //

function draw_line(x1, y1, x2, y2) {
  const line = document.createElementNS(SVGNS, 'line');
  line.setAttribute('x1', x1);
  line.setAttribute('y1', y1);
  line.setAttribute('x2', x2);
  line.setAttribute('y2', y2);
  return line;
}

function draw_square(x, y, fillColor){
    const rect = document.createElementNS(SVGNS, 'rect');
    rect.setAttribute('x', (x * SQUARE_SIZE) + 2);
    rect.setAttribute('y', (y * SQUARE_SIZE) + 2);
    rect.setAttribute('width', SQUARE_SIZE - 4);
    rect.setAttribute('height', SQUARE_SIZE - 4);
    rect.setAttribute('fill', fillColor);
    return rect;
}

function draw_mine(x, y){
    const circle = document.createElementNS(SVGNS, 'circle');
    circle.setAttribute('cx', (x + .5) * SQUARE_SIZE);
    circle.setAttribute('cy', (y + .5) * SQUARE_SIZE);
    circle.setAttribute('r',  SQUARE_SIZE / 2 - 4, 0, Math.PI*2);
    circle.setAttribute('fill', '#FF4081');
    return circle;
}

function draw_text(x, y, text){
    const textElement = document.createElementNS(SVGNS, 'text');
    textElement.setAttribute('x', (x + .5) * SQUARE_SIZE - 5);
    textElement.setAttribute('y', (y + .5) * SQUARE_SIZE + 5);
    textElement.setAttribute('fill', '#389ce2');
    textElement.setAttribute('font-family', 'Arial');
    textElement.setAttribute('font-size', '15px');
    // the entire white square will have an aria-label attribute
    textElement.setAttribute('aria-hidden', 'true');
    textElement.innerHTML = text;
    return textElement;
}

function handle_keydown(e) {
  if (e.key === 'n') {
    handle_new_game();
  }
  if (e.key === "v") {
    handle_xray_button();
  }
}
document.addEventListener("keydown", handle_keydown);
