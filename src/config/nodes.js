export const LOCATIONS = {
  hub: {
    id: 'hub',
    type: 'node',
    title: 'THE HUB',
    videoLoop: '/assets/videos/hub_loop.webm',
    uiOverlay: 'HubUI',
    exits: [
      {
        targetId: 'archive',
        label: 'ENTER ARCHIVE',
        transitionVideo: '/assets/videos/trans_hub_to_archive.webm',
        coordinates: { x: 78, y: 54 },
      },
      {
        targetId: 'manifesto',
        label: 'READ PROTOCOL',
        transitionVideo: '/assets/videos/trans_hub_to_manifesto.webm',
        coordinates: { x: 21, y: 49 },
      },
      {
        targetId: 'contact',
        label: 'OPEN CHANNEL',
        transitionVideo: '/assets/videos/trans_hub_to_contact.webm',
        coordinates: { x: 52, y: 85 },
      },
    ],
  },
  archive: {
    id: 'archive',
    type: 'node',
    title: 'ARCHIVE VAULT',
    videoLoop: '/assets/videos/archive_loop.webm',
    uiOverlay: 'ArchiveUI',
    exits: [
      {
        targetId: 'hub',
        label: 'RETURN TO HUB',
        transitionVideo: '/assets/videos/trans_archive_to_hub.webm',
        coordinates: { x: 48, y: 92 },
      },
      {
        targetId: 'manifesto',
        label: 'OPEN MANIFESTO',
        transitionVideo: '/assets/videos/trans_archive_to_manifesto.webm',
        coordinates: { x: 14, y: 42 },
      },
    ],
  },
  manifesto: {
    id: 'manifesto',
    type: 'node',
    title: 'MANIFESTO CHAMBER',
    videoLoop: '/assets/videos/manifesto_loop.webm',
    uiOverlay: 'ManifestoUI',
    exits: [
      {
        targetId: 'hub',
        label: 'BACK TO HUB',
        transitionVideo: '/assets/videos/trans_manifesto_to_hub.webm',
        coordinates: { x: 50, y: 90 },
      },
      {
        targetId: 'contact',
        label: 'PROCEED TO CONTACT',
        transitionVideo: '/assets/videos/trans_manifesto_to_contact.webm',
        coordinates: { x: 79, y: 48 },
      },
    ],
  },
  contact: {
    id: 'contact',
    type: 'node',
    title: 'CONTACT TERMINAL',
    videoLoop: '/assets/videos/contact_loop.webm',
    uiOverlay: 'ContactUI',
    exits: [
      {
        targetId: 'hub',
        label: 'DISCONNECT',
        transitionVideo: '/assets/videos/trans_contact_to_hub.webm',
        coordinates: { x: 50, y: 87 },
      },
      {
        targetId: 'archive',
        label: 'VIEW ARCHIVE',
        transitionVideo: '/assets/videos/trans_contact_to_archive.webm',
        coordinates: { x: 23, y: 53 },
      },
    ],
  },
}

export const START_NODE_ID = 'hub'
