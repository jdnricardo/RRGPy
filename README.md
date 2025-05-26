# RRGPy :bar_chart:

## New Modular Structure for Streamlit+Plotly App

This project is a fork of [this repo](https://github.com/An0n1mity/RRGPy), refactored to use Streamlit and Plotly for interactive visualization, with a modular structure for maintainability and extensibility:

```
rrgpy-streamlit/
├── README.md
├── requirements.txt
├── rrgpy.png
├── RRGIndicator.py  # (legacy, will be modularized)
├── app/
│   ├── __init__.py
│   ├── main.py           # Streamlit entrypoint
│   ├── pages/            # (optional) for multipage apps
│   ├── components/       # UI and plotting components
│   │   ├── __init__.py
│   │   └── rrg_plot.py   # Plotly RRG plot logic
│   ├── data/             # Data loading and finance logic
│   │   ├── __init__.py
│   │   └── finance.py    # RRG calculation, yfinance, etc.
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── helpers.py
└── .streamlit/
    └── config.toml       # Streamlit config (optional)
```

- **app/main.py**: Streamlit entrypoint, handles layout and user interaction.
- **app/components/**: Plotly chart and UI widgets, separated for reuse.
- **app/data/**: Data loading, yfinance, and RRG calculation logic.
- **app/utils/**: Helper functions/utilities.
- **.streamlit/**: Streamlit configuration (theme, secrets, etc.).

