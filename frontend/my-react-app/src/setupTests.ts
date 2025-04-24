import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';
// filepath: d:\lucas\Documents\Code Stuff\homebrew-application\tabletop-homebrew-app\frontend\my-react-app\src\setupTests.ts
import '@testing-library/jest-dom';

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
