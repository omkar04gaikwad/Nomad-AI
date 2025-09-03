interface ActivityTagsProps {
  activities: string[];
  className?: string;
}

export default function ActivityTags({ activities, className = '' }: ActivityTagsProps) {
  const getActivityIcon = (activity: string) => {
    const icons: { [key: string]: string } = {
      sightseeing: '👀',
      culture: '🏛️',
      food: '🍽️',
      adventure: '🏔️',
      relaxation: '🧘',
      shopping: '🛍️',
      nightlife: '🌙',
      nature: '🌿'
    };
    return icons[activity] || '🎯';
  };

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {activities.map((activity) => (
        <span
          key={activity}
          className={`activity-tag ${activity} flex items-center gap-1`}
        >
          <span>{getActivityIcon(activity)}</span>
          <span className="capitalize">{activity}</span>
        </span>
      ))}
    </div>
  );
}

