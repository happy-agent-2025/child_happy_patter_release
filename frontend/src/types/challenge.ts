export type ChallengeStatus = 'ongoing' | 'upcoming' | 'ended';

export interface ChallengeStats {
  ongoing: number;
  upcoming: number;
  totalParticipants: number;
  totalSubmissions: number;
}

export interface ChallengeItem {
  id: string;
  title: string;
  description: string;
  status: ChallengeStatus;
  reward: string;
  startDate: string;
  endDate: string;
  image: string;
}