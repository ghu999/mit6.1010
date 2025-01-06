"use strict";

// RPC wrapper
function invoke_rpc(method, args, timeout, on_done){
  $("#crash").hide();
  $("#timeout").hide();
  $("#rpc_spinner").show();
  //send RPC with whatever data is appropriate. Display an error message on crash or timeout
  var xhr = new XMLHttpRequest();
  xhr.open("POST", method, true);
  xhr.setRequestHeader('Content-Type','application/json; charset=UTF-8');
  xhr.timeout = timeout;
  xhr.send(JSON.stringify(args));
  xhr.ontimeout = function () {
    $("#timeout").show();
    $("#rpc_spinner").hide();
    $("#crash").hide();
  };
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      $("#rpc_spinner").hide();
      var result = JSON.parse(xhr.responseText)
      $("#timeout").hide();
      if (typeof(on_done) != "undefined"){
        on_done(result);
      }
    } else {
      $("#crash").show();
    }
  }
}

// Resource load wrapper
function load_resource(name, on_done) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", name, true);
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      var result = JSON.parse(xhr.responseText);
      on_done(result);
    }
  }
  xhr.send();
}

// Code that runs first
$(document).ready(function(){
    // race condition if init() does RPC on function not yet registered by restart()!
    //restart();
    //init();
    invoke_rpc( "/restart", {}, 0, function() { init(); } )
});

function restart(){
  invoke_rpc( "/restart", {} )
}

//  LAB CODE

// this is inlined into infra/ui/ui.js

const SVGNS = 'http://www.w3.org/2000/svg';
var state;
var board_size;
var board_state;
var visible_state = false;
var our_renderer = false;
var board_mask;
var board_params = {0: 5, 1: 10, 2: 15}
var current_focused_square;

var width = 300;
var height = 300;

var dug_set = new Set();
var game_over = false;

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

function init_gui(){
  const svg = document.getElementById('mySvg')

  svg.addEventListener('click', function(evt) {
    var mousePos = get_square(svg, evt);
    if (!visible_state && !game_over && !dug_set.has(mousePos.x + "|" + mousePos.y)) {
      dig_square(mousePos.y, mousePos.x);
      dug_set.add(mousePos.x + "|" + mousePos.y);
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

    if (!visible_state && !game_over && !dug_set.has(mousePos.x + "|" + mousePos.y)) {
      dig_square(mousePos.y, mousePos.x);
      dug_set.add(mousePos.x + "|" + mousePos.y);
    }

  }, false);
}

function handle_game_small_button(){
  // start small game
  init_board(0);
  document.getElementById('gameStateText').innerHTML = "NEW SMALL GAME!";
}

function handle_game_medium_button(){
  // start medium game
  init_board(1);
  document.getElementById('gameStateText').innerHTML = "NEW MEDIUM GAME!";
}

function handle_game_large_button(){
  // start large game
  init_board(2);
  document.getElementById('gameStateText').innerHTML = "NEW LARGE GAME!";
}

function handle_visible_button(){
  if (!game_over) {
    if (!visible_state) {
      document.getElementById('visible_button').innerHTML = "visible ON (v)";
      visible_state = true;
    }
    else {
      document.getElementById('visible_button').innerHTML = "visible OFF (v)";
      visible_state = false;
    }
    var args = {
      "game": board_state,
      "all_visible": visible_state,
      "our_renderer": our_renderer,
    "num_rows": board_params[board_size],
    "num_cols": board_params[board_size],
    };
    const mousePos = {
      'x': parseInt(current_focused_square?.getAttribute('data-col') ?? 0, 10),
      'y': parseInt(current_focused_square?.getAttribute('data-row') ?? 0, 10)
    }
    invoke_rpc("/ui_render_2d", args, 0, (result) => {
      render(result);
      // put focus on board square
      setTimeout(() => {
        const square = document.getElementById(`(${mousePos.y}, ${mousePos.x})`);
        if (square) {
          square.focus();
          current_focused_square = square;
        }
      }, 20);
    });
  }

}
function handle_renderer_button(){
  if (!game_over) {
    if (!our_renderer) {
      document.getElementById('renderer_button').innerHTML = "USING WORKING RENDERER";
      our_renderer = true;
    }
    else {
      document.getElementById('renderer_button').innerHTML = "USING MODULE'S RENDERER";
      our_renderer = false;
    }
    var args = {
      "game": board_state,
      "all_visible": visible_state,
      "our_renderer": our_renderer,
      "num_rows": board_params[board_size],
      "num_cols": board_params[board_size],
    };
    invoke_rpc("/ui_render_2d", args, 0, render);
  }

}

function render(result){
  // calculate unit for lattice cell

  var ux = width / board_params[board_size];
  var uy = height / board_params[board_size];
  var cx = board_params[board_size];
  var cy = board_params[board_size];


  const svg = document.getElementById('mySvg');
  svg.innerHTML = '';
  const defs = document.createElementNS(SVGNS, 'defs');
  defs.innerHTML = `
    <style>
      .grid-line {
        stroke: gray;
        stroke-width: 2;
      }
    </style>
  `;
  svg.appendChild(defs);


  var g = document.createElementNS(SVGNS, 'g');
  g.classList.add('grid-line');
  for (var x = 0; x <= cx; x += 1) {
    g.appendChild(draw_line(x * ux, 0, x * ux, width));
  }
  svg.appendChild(g);

  var g = document.createElementNS(SVGNS, 'g');
  g.classList.add('grid-line');
  for (var y = 0; y <= cy; y += 1) {
    g.appendChild(draw_line(0, y * uy, height, y * uy));
  }
  svg.appendChild(g);

  for (var row = 0; row < result.length; row++) {
    for (var col = 0; col < result[row].length; col++) {
      if (result[row][col] == '_') {
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

      if (result[row][col] == '.') {
        square.setAttribute('aria-label', `mine at (${row}, ${col}})`);
        svg.appendChild(draw_mine(col, row));
        if (!visible_state) {
          dug_set.add(col + "|" + row);
        }
      }
      else if (result[row][col] == ' ') {
        //empty cell, pass
        square.setAttribute('aria-label', `uncovered square at (${row}, ${col})`);
        if (!visible_state) {
          dug_set.add(col + "|" + row);
        }
      }
      else {
        square.setAttribute('aria-label', `uncovered square at (${row}, ${col}) with ${result[row][col]} mines around it`);
        svg.appendChild(draw_text(col, row, result[row][col]));
        if (!visible_state) {
          dug_set.add(col + "|" + row);
        }
      }
    }
  }
}

function render_result_dig(result) {
  var args = {
    "all_visible": visible_state,
    "num_rows": board_params[board_size],
    "num_cols": board_params[board_size],
      "our_renderer": our_renderer,
  };
  invoke_rpc("/ui_render_2d", args, 0, render);

  var update;
  if (result[0] == "victory") {
    update = "YOU WIN - YOU CLEARED THE BOARD!";
    game_over = true;
    var args = {
      "all_visible": true,
    "num_rows": board_params[board_size],
    "num_cols": board_params[board_size],
      "our_renderer": our_renderer,
    };
    invoke_rpc("/ui_render_2d", args, 0, render);
  }
  else if (result[0] == "defeat") {
    update = "YOU LOSE - YOU DUG A MINE!";
    game_over = true;
    var args = {
      "all_visible": true,
    "num_rows": board_params[board_size],
    "num_cols": board_params[board_size],
      "our_renderer": our_renderer,
    };
    invoke_rpc("/ui_render_2d", args, 0, render);
  }
  else if (result[0] == "ongoing") {
    update = "GOOD MOVE - YOU DUG " + result[1] + " SQUARES!";
  }
  else {
    update = "ERROR - CHECK YOUR GAME STATUS!";
  }

  document.getElementById('gameStateText').textContent = update;
  const liveUpdates = document.getElementById('liveUpdates');
  // make text different to NVDA speaks it. [] has no auditory affect
  if (liveUpdates.textContent === update) {
    update += ' [] ';
  }
  liveUpdates.textContent = update;
}

function dig_square(row, col){
  var args = {
    "game": board_state,
    "row": row,
    "col": col
  };
  invoke_rpc("/ui_dig_2d", args, 0, (result) => {
    render_result_dig(result);
    setTimeout(() => {
      const square = document.getElementById(`(${row}, ${col})`);
      if (square) {
        square.focus();
        current_focused_square = square;
      }
    }, 20);
  });
}

function render_result_new_game(result){
  board_state = result

  var args = {
    "game": board_state,
    "all_visible": visible_state,
    "num_rows": board_params[board_size],
    "num_cols": board_params[board_size],
      "our_renderer": our_renderer,
  };
  invoke_rpc("/ui_render_2d", args, 0, (result) => {
    render(result);
    // put focus on board square
    setTimeout(() => {
      const square = document.getElementById(`(0, 0)`);
      if (square) {
        square.focus();
        current_focused_square = square;
      }
    }, 20);
  });
}

function init_board(size){
  //board_size:
  //0 = small (5 x 5)
  //1 = medium (10 x 10)
  //2 = large (15 x 15)

  document.getElementById('visible_button').innerHTML = "visible OFF (v)";
  visible_state = false;
  game_over = false;
  dug_set.clear();

  var num_mines = board_params[size];
  board_size = size;
  var mine_list = [];

  var mine_set = new Set();

  for (var i = 0; i < num_mines; i++) {
    var row = Math.floor(Math.random() * (board_params[board_size]));
    var col = Math.floor(Math.random() * (board_params[board_size]));
    mine_set.add(row + "|" + col);
  }

  for (var value of mine_set) {
    var token = value.split("|");
    mine_list.push([parseInt(token[0]), parseInt(token[1])]);
  }

  var args = {
    "num_rows": board_params[board_size],
    "num_cols": board_params[board_size],
    "mines": mine_list
  };
  invoke_rpc("/ui_new_game_2d", args, 0, render_result_new_game);
}

function init(){
  init_board(0);
  init_gui();
}

function get_square(svg, evt) {
    var rect = svg.getBoundingClientRect();
    return {
        x: Math.floor((evt.clientX - rect.left) / (width / board_params[board_size])),
        y: Math.floor((evt.clientY - rect.top) / (height / board_params[board_size]))
    };
}

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
    rect.setAttribute('x', (x * width / board_params[board_size]) + 2);
    rect.setAttribute('y', (y * height / board_params[board_size]) + 2);
    rect.setAttribute('width', width / board_params[board_size] - 4);
    rect.setAttribute('height', height / board_params[board_size] - 4);
    rect.setAttribute('fill', fillColor);
    return rect;
}

function draw_mine(x, y){
    const circle = document.createElementNS(SVGNS, 'circle');
    circle.setAttribute('cx', (x * width / board_params[board_size]) + (width / board_params[board_size] / 2));
    circle.setAttribute('cy', (y * height / board_params[board_size]) + (height / board_params[board_size] / 2));
    circle.setAttribute('r',  width / board_params[board_size] / 2 - 4, 0, Math.PI*2);
    circle.setAttribute('fill', '#FF4081');
    return circle;
}


var text_settings = [
  {
    'font-size': '20px',
    'offset': 5
  },
  {
    'font-size': '15px',
    'offset': 5
  },
  {
    'font-size': '10px',
    'offset': 2.5
  }
]

function draw_text(x, y, text){
    const textElement = document.createElementNS(SVGNS, 'text');
    textElement.setAttribute('x', (x * width / board_params[board_size]) + (width / board_params[board_size] / 2) - text_settings[board_size]['offset']);
    textElement.setAttribute('y', (y * height / board_params[board_size]) + (height / board_params[board_size] / 2) + text_settings[board_size]['offset']);
    textElement.setAttribute('fill', '#389ce2');
    textElement.setAttribute('font-family', 'Arial');
    textElement.setAttribute('font-size', text_settings[board_size]['font-size']);
    // the entire white square will have an aria-label attribute
    textElement.setAttribute('aria-hidden', 'true');
    textElement.innerHTML = text;
    return textElement;
}

function handle_keydown(e) {
  if (e.key === '1') {
    handle_game_small_button();
  }
  if (e.key === '2') {
    handle_game_medium_button();
  }
  if (e.key === '3') {
    handle_game_large_button();
  }
  if (e.key === 'v') {
    handle_visible_button();
  }
}
document.addEventListener("keydown", handle_keydown);
