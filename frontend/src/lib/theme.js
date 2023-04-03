import { Roboto } from 'next/font/google'
import { createTheme } from "@mui/material";

export const roboto = Roboto({
    weight: ['300', '400', '500', '700'],
    subsets: ['latin'],
    display: 'swap',
    fallback: ['Helvetica', 'Arial', 'sans-serif'],
  });

const theme = createTheme({
    palette: {
        type: 'dark',
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

export default theme