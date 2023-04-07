import { createTheme, responsiveFontSizes } from '@mui/material'

export default function Theme() {
    const theme = createTheme({
        palette: {
        mode: 'dark',
        primary: {
            main: '#00796b',
        },
        secondary: {
            main: '#1976d2',
        },
    },
    overrides: {
        MuiAppBar: {
            colorInherit: {
                backgroundColor: '#00796b',
                color: '#fff',
            },
        },
    },
    props: {
        MuiAppBar: {
            color: 'inherit',
        },
    },
})

return responsiveFontSizes(theme);
};