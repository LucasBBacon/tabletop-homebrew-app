import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app without crashing', () => {
    render(<App />);
    const element = screen.getByText(/Vite \+ React/);
    expect(element).toBeInTheDocument();
});