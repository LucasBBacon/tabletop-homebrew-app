import { useEffect, useState } from 'react';
import socket from './socket';

function App() {
    const [ diceResult, setDiceResult ] = useState<number | null>(null);

    useEffect(() => {
        socket.on('dice-result', ({result}) => {
            setDiceResult(result);
        });

        return () => {
            socket.off('dice-result');
        };
    }, []);

    const rollDice = () => {
        socket.emit('roll-doce', { sides: 20}); // d20 roll
    };

    return (
        <div className="p-8">
            <h1 className="text-2x1 font-bold">DnD Dice Roller</h1>
            <button
                onClick={rollDice}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
            ></button>
            {diceResult !== null && <p className="mt-4">You rolled: {diceResult}</p>}
        </div>
    );
}

export default App;