import { useLocalSearchParams } from 'expo-router';
import PlayerDetailScreen from '../../features/players/PlayerDetailScreen';

export default function PlayerDetailRoute() {
  const { id } = useLocalSearchParams();
  return <PlayerDetailScreen id={Number(id)} />;
}
