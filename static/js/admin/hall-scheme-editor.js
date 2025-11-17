class HallSchemeEditor {
    constructor() {
        this.rowsInput = document.getElementById('scheme-rows');
        this.colsInput = document.getElementById('scheme-cols');
        this.applySizeButton = document.getElementById('apply-size');
        this.clearButton = document.getElementById('clear-scheme');
        this.screenTopButton = document.getElementById('screen-top');
        this.screenBottomButton = document.getElementById('screen-bottom');

        this.schemeGrid = document.getElementById('scheme-grid');
        this.rowsControls = document.getElementById('rows-controls');
        this.colsControls = document.getElementById('cols-controls');
        this.screenIndicator = document.getElementById('screen-indicator');
        this.schemeDataField = document.getElementById('id_scheme_data');

        this.rows = parseInt(this.rowsInput.value, 10) || 10;
        this.cols = parseInt(this.colsInput.value, 10) || 15;

        this.screenPosition = "top";

        this.initializeScheme();
        this.bindEvents();
    }

    bindEvents() {
        this.applySizeButton.addEventListener('click', this.applySize.bind(this));
        this.clearButton.addEventListener('click', this.clearScheme.bind(this));
        this.screenTopButton.addEventListener('click', () => this.changeScreenPosition("top"));
        this.screenBottomButton.addEventListener('click', () => this.changeScreenPosition("bottom"));
    }

    initializeScheme() {
        this.generateGrid();
        this.updateSchemeData();
    }

    generateGrid() {
        this.schemeGrid.innerHTML = '';
        this.rowsControls.innerHTML = '';
        this.colsControls.innerHTML = '';

        for (let c = 1; c <= this.cols; c++) {
            const colLabel = document.createElement('div');
            colLabel.classList.add('col-number');
            colLabel.textContent = c;
            this.colsControls.appendChild(colLabel);
        }

        for (let r = 1; r <= this.rows; r++) {
            const rowLabel = document.createElement('div');
            rowLabel.classList.add('row-number');
            rowLabel.textContent = r;
            this.rowsControls.appendChild(rowLabel);

            for (let c = 1; c <= this.cols; c++) {
                const seat = document.createElement('div');
                seat.classList.add('seat');
                seat.dataset.row = r;
                seat.dataset.col = c;

                seat.addEventListener('click', () => {
                    seat.classList.toggle('active');
                    this.updateSchemeData();
                });

                this.schemeGrid.appendChild(seat);
            }
        }
    }

    applySize() {
        this.rows = parseInt(this.rowsInput.value, 10) || this.rows;
        this.cols = parseInt(this.colsInput.value, 10) || this.cols;
        this.initializeScheme();
    }

    clearScheme() {
        const seats = this.schemeGrid.querySelectorAll('.seat');
        seats.forEach(seat => seat.classList.remove('active'));
        this.updateSchemeData();
    }

    changeScreenPosition(position) {
        this.screenPosition = position;

        this.screenTopButton.classList.toggle('active', position === "top");
        this.screenBottomButton.classList.toggle('active', position === "bottom");

        this.screenIndicator.style.order = position === "top" ? "-1" : "1";

        this.updateSchemeData();
    }

    updateSchemeData() {
        const seats = this.schemeGrid.querySelectorAll('.seat');
        const data = [];

        seats.forEach(seat => {
            data.push({
                row: parseInt(seat.dataset.row),
                col: parseInt(seat.dataset.col),
                active: seat.classList.contains('active')
            });
        });

        this.schemeDataField.value = JSON.stringify({
            rows: this.rows,
            cols: this.cols,
            screen: this.screenPosition,
            seats: data
        });
    }
}

window.HallSchemeEditor = HallSchemeEditor;
