import { useEffect, useState } from "react";
import { AcquisitionHistoryCard } from "./AcquisitionHistoryCard";
import { Skeleton } from "@/components/ui/skeleton";

interface AcquisitionHistoryProps {
  locationId: number;
}

interface AcquisitionSession {
  id: number;
  fileName: string;
  numDataPoints: number;
  startTime: string;
  endTime: string;
  sensorType: string;
  status: string;
}

export function AcquisitionHistory({ locationId }: AcquisitionHistoryProps) {
  const [sessions, setSessions] = useState<AcquisitionSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        console.log('Fetching sessions for location:', locationId);
        const response = await fetch(`/api/acquisition/sessions?locationId=${locationId}`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          throw new Error('Failed to fetch acquisition sessions');
        }
        
        const data = await response.json();
        console.log('Received sessions:', data);
        
        if (data.sessions) {
          setSessions(data.sessions);
        } else {
          console.error('No sessions array in response:', data);
          setError('Invalid response format');
        }
      } catch (err) {
        console.error('Error fetching sessions:', err);
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, [locationId]);

  if (loading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold tracking-tight">Analysis History</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-[200px]" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold tracking-tight">Analysis History</h2>
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold tracking-tight">Analysis History</h2>
        <div className="text-muted-foreground">No acquisition sessions found.</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold tracking-tight">Analysis History</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {sessions.map((session) => (
          <AcquisitionHistoryCard
            key={session.id}
            {...session}
            locationId={locationId}
          />
        ))}
      </div>
    </div>
  );
} 
