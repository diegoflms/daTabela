import { useLocalSearchParams } from 'expo-router';
import GameDetailScreen from '../../features/games/GameDetailScreen';

export default function GameDetailRoute() {
  const { id } = useLocalSearchParams();
  return <GameDetailScreen id={Number(id)} />;
}
