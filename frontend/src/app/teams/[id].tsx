import { useLocalSearchParams } from 'expo-router';
import TeamDetailScreen from '../../features/teams/TeamDetailScreen';

export default function TeamDetailRoute() {
  const { id } = useLocalSearchParams();
  return <TeamDetailScreen id={Number(id)} />;
}
