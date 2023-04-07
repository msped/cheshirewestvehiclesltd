import CssBaseline from '@mui/material/CssBaseline'
import { ThemeProvider } from '@mui/material/styles'

import Theme from './theme'

function App() {
  return (
    <ThemeProvider theme={Theme()}>
      <CssBaseline />
    </ThemeProvider>
  );
}

export default App;
