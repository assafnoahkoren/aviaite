import Chat from './components/Chat';
import './App.css';

function App() {
  return (
    <div className="flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 min-h-dvh w-full h-dvh">
      <div className="flex flex-col w-full h-dvh text-center">
        <Chat />
      </div>
    </div>
  );
}

export default App;
